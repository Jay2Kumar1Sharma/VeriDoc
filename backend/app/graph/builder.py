from collections.abc import Awaitable, Callable
from typing import Literal

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from app.core.config import Settings, get_settings
from app.graph.nodes.fallback import fallback_node
from app.graph.nodes.generator import generator_node
from app.graph.nodes.grader import grader_node
from app.graph.nodes.hallucination_check import hallucination_check_node
from app.graph.nodes.query_analysis import query_analysis_node
from app.graph.nodes.retrieval import retrieval_node
from app.graph.nodes.rewriter import rewriter_node
from app.graph.nodes.web_search import WebSearchClient, web_search_node
from app.graph.state import RAGState
from app.llm.clients import LLMClient, get_llm_client
from app.stores.vector_store import ChromaVectorStore, VectorStore

NodeResult = dict[str, object]
NodeCallable = Callable[[RAGState], Awaitable[NodeResult]]


def build_graph(
    llm_client: LLMClient | None = None,
    vector_store: VectorStore | None = None,
    web_search_client: WebSearchClient | None = None,
    settings: Settings | None = None,
):
    resolved_settings = settings or get_settings()
    resolved_llm = llm_client or get_llm_client(resolved_settings)
    resolved_vector_store = vector_store or ChromaVectorStore(settings=resolved_settings)

    async def run_query_analysis(state: RAGState) -> NodeResult:
        return await query_analysis_node(state, resolved_llm, resolved_settings)

    async def run_retrieval(state: RAGState) -> NodeResult:
        return await retrieval_node(state, resolved_vector_store, resolved_settings)

    async def run_grader(state: RAGState) -> NodeResult:
        return await grader_node(state, resolved_llm, resolved_settings)

    async def run_rewriter(state: RAGState) -> NodeResult:
        return await rewriter_node(state, resolved_llm, resolved_settings)

    async def run_generator(state: RAGState) -> NodeResult:
        return await generator_node(state, resolved_llm, resolved_settings)

    async def run_groundedness_check(state: RAGState) -> NodeResult:
        return await hallucination_check_node(state, resolved_llm, resolved_settings)

    async def run_web_search(state: RAGState) -> NodeResult:
        return await web_search_node(state, resolved_settings, web_search_client)

    graph = StateGraph(RAGState)
    graph.add_node("query_analysis", _node(run_query_analysis))
    graph.add_node("retrieval", _node(run_retrieval))
    graph.add_node("grader", _node(run_grader))
    graph.add_node("rewriter", _node(run_rewriter))
    graph.add_node("generate", _node(run_generator))
    graph.add_node("groundedness_check", _node(run_groundedness_check))
    graph.add_node("web_search", _node(run_web_search))
    graph.add_node("fallback", _node(fallback_node))

    graph.add_edge(START, "query_analysis")
    graph.add_edge("query_analysis", "retrieval")
    graph.add_edge("retrieval", "grader")
    graph.add_conditional_edges(
        "grader",
        route_after_grading,
        {
            "generate": "generate",
            "rewrite": "rewriter",
            "web_search": "web_search",
            "fallback": "fallback",
        },
    )
    graph.add_edge("rewriter", "retrieval")
    graph.add_edge("web_search", "grader")
    graph.add_edge("generate", "groundedness_check")
    graph.add_conditional_edges(
        "groundedness_check",
        route_after_hallucination_check,
        {"end": END, "rewrite": "rewriter"},
    )
    graph.add_edge("fallback", END)
    return graph.compile(checkpointer=MemorySaver())


def route_after_grading(
    state: RAGState,
) -> Literal["generate", "rewrite", "web_search", "fallback"]:
    if state["relevant_docs"]:
        return "generate"
    if state["retry_count"] < state["max_retries"]:
        return "rewrite"
    if state["web_search_enabled"] and not state["web_search_attempted"]:
        return "web_search"
    return "fallback"


def route_after_hallucination_check(state: RAGState) -> Literal["end", "rewrite"]:
    check = state["hallucination_check"] or {}
    if check.get("grounded") is not False:
        return "end"
    if state["retry_count"] < state["max_retries"]:
        return "rewrite"
    return "end"


def _node(func: NodeCallable) -> NodeCallable:
    return func
