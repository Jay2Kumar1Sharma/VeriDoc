from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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

    @app.get("/health", tags=["health"])
    async def health() -> dict[str, str]:
        return {
            "status": "ok",
            "version": settings.app_version,
            "env": settings.env,
        }

    return app


app = create_app()

