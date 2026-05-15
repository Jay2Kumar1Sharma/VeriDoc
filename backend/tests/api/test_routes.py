import json
from collections.abc import AsyncIterator, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.deps import get_graph, get_vector_store
from app.ingestion.chunker import Chunk
from app.main import create_app
from app.schemas.types import Citation, RetrievedDoc
from app.stores.metadata_store import MetadataStore


class FakeGraph:
    async def ainvoke(
        self,
        input: dict[str, Any],
        config: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        del config
        return {
            **input,
            "query_type": "how-to",
            "answer": "Use path parameters with braces. [#chunk_1]",
            "retry_count": 1,
            "hallucination_check": {"grounded": True, "unsupported_claims": []},
            "citations": [
                Citation(
                    chunk_id="chunk_1",
                    source="test.md",
                    title="Test",
                    snippet="Path parameters use braces.",
                    header_path=["Tutorial"],
                )
            ],
            "trace": [{"node": "query_analysis", "duration_ms": 1, "output": {}}],
        }


class FakeVectorStore:
    def __init__(self) -> None:
        self.deleted_sources: list[str] = []

    def add_chunks(self, chunks: Sequence[Chunk]) -> None:
        del chunks

    def similarity_search(
        self,
        query: str,
        k: int,
        filter: dict[str, Any] | None = None,
    ) -> list[RetrievedDoc]:
        del query, k, filter
        return []

    def delete_by_source(self, source: str) -> None:
        self.deleted_sources.append(source)

    def count(self) -> int:
        return 0


@pytest.fixture
async def client(tmp_path: Path) -> AsyncIterator[AsyncClient]:
    app = create_app()
    store = MetadataStore(str(tmp_path / "app.db"))
    await store.migrate()
    vector_store = FakeVectorStore()
    app.state.metadata_store = store
    app.state.vector_store = vector_store
    app.state.ingest_jobs = {}

    async def graph_override() -> AsyncIterator[FakeGraph]:
        yield FakeGraph()

    app.dependency_overrides[get_graph] = graph_override
    app.dependency_overrides[get_vector_store] = lambda: vector_store
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_query_happy_path_persists_trace(client: AsyncClient) -> None:
    response = await client.post("/query", json={"question": "How do path params work?"})

    assert response.status_code == 200
    body = response.json()
    assert body["answer"].endswith("[#chunk_1]")
    assert body["citations"][0]["chunk_id"] == "chunk_1"
    assert response.headers["X-Trace-Id"] == body["trace_id"]

    trace_response = await client.get(f"/traces/{body['trace_id']}")
    assert trace_response.status_code == 200
    assert trace_response.json()["trace_steps"][0]["node"] == "query_analysis"


@pytest.mark.asyncio
async def test_query_validation_error_shape(client: AsyncClient) -> None:
    response = await client.post("/query", json={"question": ""})

    assert response.status_code == 422
    assert response.json()["title"] == "Validation Error"
    assert "X-Trace-Id" in response.headers


@pytest.mark.asyncio
async def test_feedback_requires_existing_trace(client: AsyncClient) -> None:
    missing = await client.post("/feedback", json={"trace_id": "missing", "rating": 1})
    assert missing.status_code == 404

    query_response = await client.post("/query", json={"question": "How?"})
    trace_id = query_response.json()["trace_id"]
    feedback = await client.post("/feedback", json={"trace_id": trace_id, "rating": -1})

    assert feedback.status_code == 204


@pytest.mark.asyncio
async def test_documents_list_and_delete(client: AsyncClient, tmp_path: Path) -> None:
    store = client._transport.app.state.metadata_store  # type: ignore[attr-defined]
    await store.upsert_document(
        doc_id="doc_1",
        source="source.md",
        title="Source",
        chunk_count=2,
        status="ingested",
        ingested_at=datetime.now(UTC),
    )

    list_response = await client.get("/documents")
    assert list_response.status_code == 200
    assert list_response.json()["documents"][0]["doc_id"] == "doc_1"

    delete_response = await client.delete("/documents/doc_1")
    assert delete_response.status_code == 204
    assert await store.get_document("doc_1") is None


@pytest.mark.asyncio
async def test_not_found_paths(client: AsyncClient) -> None:
    trace_response = await client.get("/traces/missing")
    document_response = await client.delete("/documents/missing")
    job_response = await client.get("/ingest/jobs/missing")

    assert trace_response.status_code == 404
    assert document_response.status_code == 404
    assert job_response.status_code == 404


@pytest.mark.asyncio
async def test_ingest_single_file_upload(client: AsyncClient) -> None:
    response = await client.post(
        "/ingest",
        files={"files": ("guide.md", b"# Guide\n\nUploaded content.", "text/markdown")},
    )

    assert response.status_code == 202
    assert response.json()["ingested"][0]["chunk_count"] >= 1


@pytest.mark.asyncio
async def test_ingest_multiple_urls_returns_job(client: AsyncClient) -> None:
    response = await client.post(
        "/ingest",
        json={"urls": ["https://example.test/a", "https://example.test/b"]},
    )

    assert response.status_code == 202
    assert response.json()["job_id"]


@pytest.mark.asyncio
async def test_sse_query_shape(client: AsyncClient) -> None:
    response = await client.post(
        "/query",
        json={"question": "Stream?"},
        headers={"accept": "text/event-stream"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert "data:" in response.text
    assert json.loads(response.text.strip().split("data: ")[-1])["done"] is True

