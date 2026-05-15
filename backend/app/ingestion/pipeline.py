import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from app.core.config import Settings, get_settings
from app.core.logging import get_logger
from app.ingestion.chunker import StructureAwareChunker
from app.ingestion.loaders import Document, HTMLLoader, MarkdownLoader
from app.stores.metadata_store import MetadataStore
from app.stores.vector_store import ChromaVectorStore, VectorStore

logger = get_logger(__name__)


@dataclass(frozen=True)
class IngestionResult:
    source: str
    doc_id: str | None
    chunk_count: int
    status: Literal["ingested", "skipped", "failed"]
    error: str | None = None


@dataclass(frozen=True)
class IngestionReport:
    results: list[IngestionResult]

    @property
    def ingested(self) -> list[IngestionResult]:
        return [result for result in self.results if result.status == "ingested"]

    @property
    def failed(self) -> list[IngestionResult]:
        return [result for result in self.results if result.status == "failed"]


async def ingest_sources(
    sources: list[str | Path],
    replace: bool = True,
    settings: Settings | None = None,
    metadata_store: MetadataStore | None = None,
    vector_store: VectorStore | None = None,
    markdown_loader: MarkdownLoader | None = None,
    html_loader: HTMLLoader | None = None,
) -> IngestionReport:
    resolved_settings = settings or get_settings()
    resolved_metadata_store = metadata_store or MetadataStore(resolved_settings.sqlite_path)
    resolved_vector_store = vector_store or ChromaVectorStore(settings=resolved_settings)
    chunker = StructureAwareChunker(
        chunk_size=resolved_settings.chunk_size,
        chunk_overlap=resolved_settings.chunk_overlap,
    )
    await resolved_metadata_store.migrate()

    results: list[IngestionResult] = []
    for source in sources:
        source_text = str(source)
        doc_id = document_id(source_text)
        try:
            existing = await resolved_metadata_store.get_document_by_source(source_text)
            if existing is not None and not replace:
                results.append(
                    IngestionResult(
                        source=source_text,
                        doc_id=existing.doc_id,
                        chunk_count=existing.chunk_count,
                        status="skipped",
                    )
                )
                continue

            document = load_source(source, markdown_loader, html_loader)
            chunks = chunker.chunk(document)
            if replace and existing is not None:
                resolved_vector_store.delete_by_source(source_text)
                await resolved_metadata_store.delete_document_by_source(source_text)

            resolved_vector_store.add_chunks(chunks)
            await resolved_metadata_store.upsert_document(
                doc_id=doc_id,
                source=document.source,
                title=document.title,
                chunk_count=len(chunks),
                status="ingested",
                ingested_at=document.fetched_at,
            )
            results.append(
                IngestionResult(
                    source=document.source,
                    doc_id=doc_id,
                    chunk_count=len(chunks),
                    status="ingested",
                )
            )
            logger.info("source_ingested", source=document.source, chunk_count=len(chunks))
        except Exception as exc:
            logger.exception("source_ingestion_failed", source=source_text, error=str(exc))
            results.append(
                IngestionResult(
                    source=source_text,
                    doc_id=doc_id,
                    chunk_count=0,
                    status="failed",
                    error=str(exc),
                )
            )
    return IngestionReport(results=results)


def load_source(
    source: str | Path,
    markdown_loader: MarkdownLoader | None = None,
    html_loader: HTMLLoader | None = None,
) -> Document:
    source_text = str(source)
    if source_text.startswith(("http://", "https://")):
        return (html_loader or HTMLLoader()).load(source_text)
    return (markdown_loader or MarkdownLoader()).load(Path(source))


def document_id(source: str) -> str:
    return f"doc_{hashlib.sha256(source.encode('utf-8')).hexdigest()}"

