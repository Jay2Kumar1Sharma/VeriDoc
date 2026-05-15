from operator import add
from typing import Annotated, Literal, TypedDict

from app.schemas.types import Citation, GradingResult, RetrievedDoc


class RAGState(TypedDict):
    original_query: str
    session_id: str | None
    conversation_context: str
    rewritten_query: str
    query_type: Literal["conceptual", "how-to", "troubleshooting", "api-reference"]
    retrieved_docs: list[RetrievedDoc]
    relevant_docs: list[RetrievedDoc]
    grading_results: list[GradingResult]
    retry_count: int
    max_retries: int
    route_decision: Literal["generate", "rewrite", "web_search", "fallback"]
    web_search_enabled: bool
    web_search_attempted: bool
    answer: str
    citations: list[Citation]
    hallucination_check: dict[str, object] | None
    trace: Annotated[list[dict[str, object]], add]
    error: str | None


def initial_state(
    question: str,
    session_id: str | None = None,
    max_retries: int = 2,
    conversation_context: str = "",
    web_search_enabled: bool = False,
) -> RAGState:
    return {
        "original_query": question,
        "session_id": session_id,
        "conversation_context": conversation_context,
        "rewritten_query": question,
        "query_type": "conceptual",
        "retrieved_docs": [],
        "relevant_docs": [],
        "grading_results": [],
        "retry_count": 0,
        "max_retries": max_retries,
        "route_decision": "generate",
        "web_search_enabled": web_search_enabled,
        "web_search_attempted": False,
        "answer": "",
        "citations": [],
        "hallucination_check": None,
        "trace": [],
        "error": None,
    }
