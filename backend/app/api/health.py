from importlib import import_module
from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_settings_dep
from app.core.config import Settings
from app.schemas.api import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health(settings: Annotated[Settings, Depends(get_settings_dep)]) -> HealthResponse:
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        env=settings.env,
        vector_store_chunks=_chroma_count(settings.chroma_persist_dir),
        llm_provider=settings.llm_provider,
        embedding_provider=settings.embedding_provider,
    )


def _chroma_count(path: str) -> int:
    try:
        chromadb = import_module("chromadb")
        client = chromadb.PersistentClient(path=path)
        return int(client.get_or_create_collection("docs").count())
    except Exception:
        return 0
