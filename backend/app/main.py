from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import documents, feedback, health, ingest, query, sessions, traces
from app.core.config import Settings, get_settings
from app.core.logging import configure_logging, get_logger, trace_id_var
from app.stores.metadata_store import MetadataStore

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings: Settings = app.state.settings
    store = MetadataStore(settings.sqlite_path)
    await store.migrate()
    app.state.metadata_store = store
    logger.info("metadata_store_migrated", sqlite_path=settings.sqlite_path)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Self-corrective RAG assistant for technical documentation.",
        lifespan=lifespan,
    )
    app.state.settings = settings
    app.state.ingest_jobs = {}

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def trace_middleware(request: Request, call_next):  # type: ignore[no-untyped-def]
        trace_id = str(uuid4())
        token = trace_id_var.set(trace_id)
        try:
            response = await call_next(request)
            response.headers["X-Trace-Id"] = trace_id
            return response
        except Exception as exc:
            logger.exception("unhandled_request_error", error=str(exc))
            return JSONResponse(
                status_code=500,
                content={
                    "type": "about:blank",
                    "title": "Internal Server Error",
                    "status": 500,
                    "detail": "An unexpected error occurred.",
                    "trace_id": trace_id,
                },
                headers={"X-Trace-Id": trace_id},
            )
        finally:
            trace_id_var.reset(token)

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
        trace_id = trace_id_var.get()
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "type": "about:blank",
                "title": "HTTP Error",
                "status": exc.status_code,
                "detail": exc.detail,
                "trace_id": trace_id,
            },
            headers={"X-Trace-Id": trace_id or ""},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        trace_id = trace_id_var.get()
        return JSONResponse(
            status_code=422,
            content={
                "type": "about:blank",
                "title": "Validation Error",
                "status": 422,
                "detail": exc.errors(),
                "trace_id": trace_id,
            },
            headers={"X-Trace-Id": trace_id or ""},
        )

    app.include_router(health.router)
    app.include_router(query.router)
    app.include_router(ingest.router)
    app.include_router(documents.router)
    app.include_router(feedback.router)
    app.include_router(traces.router)
    app.include_router(sessions.router)

    return app


app = create_app()
