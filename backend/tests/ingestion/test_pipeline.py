from collections.abc import Sequence
from pathlib import Path
from typing import Any

import pytest

from app.ingestion.chunker import Chunk
from app.ingestion.loaders import HTMLLoader
from app.ingestion.pipeline import ingest_sources
from app.schemas.types import RetrievedDoc
from app.stores.metadata_store import MetadataStore


class FakeVectorStore:
    def __init__(self) -> None:
        self.chunks_by_id: dict[str, Chunk] = {}

    def add_chunks(self, chunks: Sequence[Chunk]) -> None:
        for chunk in chunks:
            self.chunks_by_id[str(chunk.metadata["chunk_id"])] = chunk

    def similarity_search(
        self,
        query: str,
        k: int,
        filter: dict[str, Any] | None = None,
    ) -> list[RetrievedDoc]:
        return []

    def delete_by_source(self, source: str) -> None:
        for chunk_id, chunk in list(self.chunks_by_id.items()):
            if chunk.metadata["source"] == source:
                del self.chunks_by_id[chunk_id]

    def count(self) -> int:
        return len(self.chunks_by_id)


class FailingHTMLLoader(HTMLLoader):
    def load(self, url: str):  # type: ignore[no-untyped-def]
        raise RuntimeError(f"cannot fetch {url}")


@pytest.mark.asyncio
async def test_pipeline_is_idempotent_for_replace(tmp_path: Path) -> None:
    path = tmp_path / "guide.md"
    path.write_text("# Guide\n\nUse the API carefully.", encoding="utf-8")
    metadata_store = MetadataStore(str(tmp_path / "app.db"))
    vector_store = FakeVectorStore()

    first = await ingest_sources([path], metadata_store=metadata_store, vector_store=vector_store)
    first_ids = sorted(vector_store.chunks_by_id)
    second = await ingest_sources([path], metadata_store=metadata_store, vector_store=vector_store)
    second_ids = sorted(vector_store.chunks_by_id)

    assert first.results[0].status == "ingested"
    assert second.results[0].status == "ingested"
    assert first_ids == second_ids
    assert await metadata_store.document_count() == 1


@pytest.mark.asyncio
async def test_pipeline_isolates_source_errors(tmp_path: Path) -> None:
    path = tmp_path / "guide.md"
    path.write_text("# Guide\n\nWorking source.", encoding="utf-8")
    metadata_store = MetadataStore(str(tmp_path / "app.db"))
    vector_store = FakeVectorStore()

    report = await ingest_sources(
        ["https://bad.example.test/docs", path],
        metadata_store=metadata_store,
        vector_store=vector_store,
        html_loader=FailingHTMLLoader(),
    )

    assert [result.status for result in report.results] == ["failed", "ingested"]
    assert await metadata_store.document_count() == 1
    assert vector_store.count() == 1


@pytest.mark.asyncio
async def test_pipeline_records_correct_chunk_count(tmp_path: Path) -> None:
    path = tmp_path / "guide.md"
    path.write_text(
        "# Guide\n\n" + " ".join(f"word{index}" for index in range(200)),
        encoding="utf-8",
    )
    metadata_store = MetadataStore(str(tmp_path / "app.db"))
    vector_store = FakeVectorStore()

    report = await ingest_sources([path], metadata_store=metadata_store, vector_store=vector_store)
    record = await metadata_store.get_document_by_source(str(path))

    assert record is not None
    assert record.chunk_count == report.results[0].chunk_count
    assert record.chunk_count == vector_store.count()
