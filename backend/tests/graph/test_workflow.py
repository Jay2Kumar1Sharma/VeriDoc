from collections.abc import Sequence
from typing import Any

import pytest
from pydantic import BaseModel

from app.core.config import Settings
from app.graph.builder import build_graph
from app.graph.nodes.fallback import FALLBACK_ANSWER
from app.graph.state import initial_state
from app.llm.clients import ChatMessage
from app.llm.prompts import GradingOutput, GroundednessOutput, QueryAnalysisOutput, RewriteOutput
from app.schemas.types import RetrievedDoc


class FakeLLMClient:
    def __init__(
        self,
        relevant_by_doc: dict[str, bool] | None = None,
        grounded: list[bool] | None = None,
    ) -> None:
        self.relevant_by_doc = relevant_by_doc or {}
        self.grounded = grounded or [True]
        self.grounded_calls = 0
        self.rewrite_calls = 0

    async def complete(
        self,
        messages: Sequence[ChatMessage],
        model: str,
        response_model: type[BaseModel] | None = None,
        temperature: float = 0,
    ) -> str | BaseModel:
        del model, temperature
        if response_model is QueryAnalysisOutput:
            return QueryAnalysisOutput(
                rewritten_query="rewritten docs query",
                query_type="how-to",
            )
        if response_model is GradingOutput:
            user_content = messages[-1].content
            relevant = any(
                chunk_id in user_content and is_relevant
                for chunk_id, is_relevant in self.relevant_by_doc.items()
            )
            return GradingOutput(relevant=relevant, reasoning="matched" if relevant else "no match")
        if response_model is RewriteOutput:
            self.rewrite_calls += 1
            return RewriteOutput(
                rewritten_query=f"better query {self.rewrite_calls}",
                reasoning="narrowed search",
            )
        if response_model is GroundednessOutput:
            index = min(self.grounded_calls, len(self.grounded) - 1)
            self.grounded_calls += 1
            grounded = self.grounded[index]
            return GroundednessOutput(
                grounded=grounded,
                unsupported_claims=[] if grounded else ["unsupported detail"],
            )
        return "Use FastAPI path parameters with braces. [#doc_1]"


class FakeVectorStore:
    def __init__(self, batches: list[list[RetrievedDoc]]) -> None:
        self._batches = batches
        self.calls = 0

    def add_chunks(self, chunks: Sequence[Any]) -> None:
        del chunks

    def similarity_search(
        self,
        query: str,
        k: int,
        filter: dict[str, Any] | None = None,
    ) -> list[RetrievedDoc]:
        del query, k, filter
        index = min(self.calls, len(self._batches) - 1)
        self.calls += 1
        return self._batches[index]

    def delete_by_source(self, source: str) -> None:
        del source

    def count(self) -> int:
        return sum(len(batch) for batch in self._batches)


def doc(chunk_id: str, content: str = "Path params use braces.") -> RetrievedDoc:
    return RetrievedDoc(
        chunk_id=chunk_id,
        content=content,
        metadata={
            "source": "test.md",
            "title": "Test Docs",
            "h1": "Tutorial",
            "h2": "Path Params",
            "h3": "",
        },
        score=0.9,
    )


def settings(max_retries: int = 2) -> Settings:
    return Settings(
        GEMINI_API_KEY="test-key",
        LLM_PROVIDER="gemini",
        GENERATION_MODEL="gemini-2.5-flash-lite",
        GRADING_MODEL="gemini-2.5-flash-lite",
        MAX_RETRIES=max_retries,
        TOP_K=5,
    )


@pytest.mark.asyncio
async def test_happy_path_generates_cited_answer() -> None:
    graph = build_graph(
        llm_client=FakeLLMClient(relevant_by_doc={"doc_1": True}),
        vector_store=FakeVectorStore([[doc("doc_1")]]),
        settings=settings(),
    )

    result = await graph.ainvoke(
        initial_state("How do I use path params?"),
        config={"configurable": {"thread_id": "happy"}},
    )

    assert result["answer"].endswith("[#doc_1]")
    assert result["citations"][0].chunk_id == "doc_1"
    assert result["retry_count"] == 0


@pytest.mark.asyncio
async def test_rewrite_loop_finds_relevant_docs_second_try() -> None:
    graph = build_graph(
        llm_client=FakeLLMClient(relevant_by_doc={"doc_1": True}),
        vector_store=FakeVectorStore([[doc("doc_0")], [doc("doc_1")]]),
        settings=settings(),
    )

    result = await graph.ainvoke(
        initial_state("How do I use path params?"),
        config={"configurable": {"thread_id": "rewrite"}},
    )

    assert result["answer"].endswith("[#doc_1]")
    assert result["retry_count"] == 1


@pytest.mark.asyncio
async def test_max_retries_fallback() -> None:
    graph = build_graph(
        llm_client=FakeLLMClient(relevant_by_doc={}),
        vector_store=FakeVectorStore([[doc("doc_0")], [doc("doc_2")]]),
        settings=settings(max_retries=1),
    )

    result = await graph.ainvoke(
        initial_state("Unknown thing?", max_retries=1),
        config={"configurable": {"thread_id": "fallback"}},
    )

    assert result["answer"] == FALLBACK_ANSWER
    assert result["retry_count"] == 1


@pytest.mark.asyncio
async def test_hallucination_retry_triggers_retrieval() -> None:
    vector_store = FakeVectorStore([[doc("doc_1")], [doc("doc_1")]])
    graph = build_graph(
        llm_client=FakeLLMClient(relevant_by_doc={"doc_1": True}, grounded=[False, True]),
        vector_store=vector_store,
        settings=settings(max_retries=2),
    )

    result = await graph.ainvoke(
        initial_state("How do I use path params?", max_retries=2),
        config={"configurable": {"thread_id": "hallucination"}},
    )

    assert result["hallucination_check"]["grounded"] is True
    assert result["retry_count"] == 1
    assert vector_store.calls == 2


@pytest.mark.asyncio
async def test_trace_contains_executed_nodes_and_retry_bound() -> None:
    graph = build_graph(
        llm_client=FakeLLMClient(relevant_by_doc={"doc_1": True}),
        vector_store=FakeVectorStore([[doc("doc_1")]]),
        settings=settings(max_retries=2),
    )

    result = await graph.ainvoke(
        initial_state("How do I use path params?", max_retries=2),
        config={"configurable": {"thread_id": "trace"}},
    )

    node_names = [entry["node"] for entry in result["trace"]]

    assert node_names == [
        "query_analysis",
        "retrieval",
        "grader",
        "generator",
        "hallucination_check",
    ]
    assert result["retry_count"] <= result["max_retries"]


@pytest.mark.asyncio
async def test_citations_reference_real_relevant_docs() -> None:
    graph = build_graph(
        llm_client=FakeLLMClient(relevant_by_doc={"doc_1": True}),
        vector_store=FakeVectorStore([[doc("doc_1")]]),
        settings=settings(),
    )

    result = await graph.ainvoke(
        initial_state("How do I use path params?"),
        config={"configurable": {"thread_id": "citations"}},
    )

    relevant_ids = {retrieved.chunk_id for retrieved in result["relevant_docs"]}
    citation_ids = {citation.chunk_id for citation in result["citations"]}

    assert citation_ids <= relevant_ids
