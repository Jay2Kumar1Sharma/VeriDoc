import uuid
from pathlib import Path
from typing import Annotated, Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from pydantic import ValidationError

from app.api.deps import get_metadata_store, get_settings_dep, get_vector_store
from app.core.config import Settings
from app.ingestion.pipeline import ingest_sources
from app.schemas.api import IngestJobResponse, IngestResponse, IngestResult, IngestUrlsRequest
from app.stores.metadata_store import MetadataStore
from app.stores.vector_store import VectorStore

router = APIRouter(prefix="/ingest", tags=["ingest"])
REPO_ROOT = Path(__file__).resolve().parents[3]


@router.post("", response_model=IngestResponse, status_code=status.HTTP_202_ACCEPTED)
async def ingest(
    request: Request,
    background_tasks: BackgroundTasks,
    settings: Annotated[Settings, Depends(get_settings_dep)],
    metadata_store: Annotated[MetadataStore, Depends(get_metadata_store)],
    vector_store: Annotated[VectorStore, Depends(get_vector_store)],
) -> IngestResponse:
    sources = await _extract_sources(request)
    if not sources:
        raise HTTPException(status_code=422, detail="Provide at least one URL or uploaded file.")

    if len(sources) == 1:
        report = await ingest_sources(
            sources,
            settings=settings,
            metadata_store=metadata_store,
            vector_store=vector_store,
        )
        return _response_from_report(report.results)

    job_id = str(uuid.uuid4())
    request.app.state.ingest_jobs[job_id] = IngestJobResponse(job_id=job_id, status="queued")
    background_tasks.add_task(
        _run_job,
        request.app.state.ingest_jobs,
        job_id,
        sources,
        settings,
        metadata_store,
        vector_store,
    )
    return IngestResponse(job_id=job_id, status="queued")


@router.get("/jobs/{job_id}", response_model=IngestJobResponse)
async def get_job(job_id: str, request: Request) -> IngestJobResponse:
    job = request.app.state.ingest_jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Ingestion job not found.")
    return job


async def _extract_sources(request: Request) -> list[str | Path]:
    content_type = request.headers.get("content-type", "")
    if content_type.startswith("multipart/form-data"):
        form = await request.form()
        upload_dir = REPO_ROOT / "corpus" / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)
        sources: list[str | Path] = []
        for item in form.getlist("files"):
            if not hasattr(item, "filename") or not hasattr(item, "read"):
                continue
            filename = str(item.filename or "upload.md")
            target = upload_dir / f"{uuid.uuid4()}_{Path(filename).name}"
            target.write_bytes(await item.read())
            sources.append(target)
        return sources
    data: dict[str, Any] = await request.json()
    try:
        payload = IngestUrlsRequest.model_validate(data)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc
    return [str(url) for url in payload.urls]


async def _run_job(
    jobs: dict[str, IngestJobResponse],
    job_id: str,
    sources: list[str | Path],
    settings: Settings,
    metadata_store: MetadataStore,
    vector_store: VectorStore,
) -> None:
    jobs[job_id] = IngestJobResponse(job_id=job_id, status="running")
    try:
        report = await ingest_sources(
            sources,
            settings=settings,
            metadata_store=metadata_store,
            vector_store=vector_store,
        )
        response = _job_response_from_results(job_id, report.results)
        jobs[job_id] = response
    except Exception as exc:
        jobs[job_id] = IngestJobResponse(job_id=job_id, status="failed", error=str(exc))


def _response_from_report(results: list[Any]) -> IngestResponse:
    ingested = [_ingest_result(result) for result in results if result.status == "ingested"]
    failed = [_ingest_result(result) for result in results if result.status == "failed"]
    return IngestResponse(ingested=ingested, failed=failed, status="completed")


def _job_response_from_results(job_id: str, results: list[Any]) -> IngestJobResponse:
    response = _response_from_report(results)
    return IngestJobResponse(
        job_id=job_id,
        status="completed",
        ingested=response.ingested,
        failed=response.failed,
    )


def _ingest_result(result: Any) -> IngestResult:
    return IngestResult(
        source=str(result.source),
        doc_id=result.doc_id,
        chunk_count=int(result.chunk_count),
        status=str(result.status),
        error=result.error,
    )
