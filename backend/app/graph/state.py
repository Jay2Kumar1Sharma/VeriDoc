from operator import add
from typing import Annotated, Literal, TypedDict

from app.schemas.types import Citation, GradingResult, RetrievedDoc


class RAGState(TypedDict):
    original_query: str
    session_id: str | None
    rewritten_query: str
    query_type: Literal["conceptual", "how-to", "troubleshooting", "api-reference"]
    retrieved_docs: list[RetrievedDoc]
    relevant_docs: list[RetrievedDoc]
    grading_results: list[GradingResult]
    retry_count: int
    max_retries: int
    route_decision: Literal["generate", "rewrite", "fallback"]
    answer: str
    citations: list[Citation]
    hallucination_check: dict[str, object] | None
    trace: Annotated[list[dict[str, object]], add]
    error: str | None


def initial_state(
    question: str,
    session_id: str | None = None,
    max_retries: int = 2,
) -> RAGState:
    return {
        "original_query": question,
        "session_id": session_id,
        "rewritten_query": question,
        "query_type": "conceptual",
        "retrieved_docs": [],
        "relevant_docs": [],
        "grading_results": [],
        "retry_count": 0,
        "max_retries": max_retries,
        "route_decision": "generate",
        "answer": "",
        "citations": [],
        "hallucination_check": None,
        "trace": [],
        "error": None,
    }

