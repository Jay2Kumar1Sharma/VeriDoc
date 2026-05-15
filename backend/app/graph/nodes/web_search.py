import re
from dataclasses import dataclass
from typing import Protocol

import httpx

from app.core.config import Settings
from app.graph.nodes.common import NodeTimer, trace_entry
from app.graph.state import RAGState
from app.schemas.types import RetrievedDoc

SLUG_RE = re.compile(r"[^a-z0-9]+")


@dataclass(frozen=True)
class WebSearchResult:
    title: str
    url: str
    content: str
    score: float


class WebSearchClient(Protocol):
    async def search(self, query: str, max_results: int) -> list[WebSearchResult]: ...


class TavilyWebSearchClient:
    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    async def search(self, query: str, max_results: int) -> list[WebSearchResult]:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": self._api_key,
                    "query": query,
                    "search_depth": "basic",
                    "max_results": max_results,
                },
            )
            response.raise_for_status()
        payload = response.json()
        results: list[WebSearchResult] = []
        for item in payload.get("results", []):
            results.append(
                WebSearchResult(
                    title=str(item.get("title", "Web result")),
                    url=str(item.get("url", "")),
                    content=str(item.get("content", "")),
                    score=float(item.get("score", 0.0)),
                )
            )
        return results


async def web_search_node(
    state: RAGState,
    settings: Settings,
    client: WebSearchClient | None = None,
) -> dict[str, object]:
    timer = NodeTimer()
    if client is None:
        if not settings.tavily_api_key:
            return {
                "retrieved_docs": [],
                "web_search_attempted": True,
                "trace": [
                    trace_entry(
                        "web_search",
                        timer.elapsed_ms(),
                        {"query": state["rewritten_query"], "status": "missing_tavily_api_key"},
                    )
                ],
            }
        client = TavilyWebSearchClient(settings.tavily_api_key)

    results = await client.search(state["rewritten_query"], settings.web_search_max_results)
    docs = [_result_to_doc(result, index) for index, result in enumerate(results)]
    return {
        "retrieved_docs": docs,
        "web_search_attempted": True,
        "trace": [
            trace_entry(
                "web_search",
                timer.elapsed_ms(),
                {
                    "query": state["rewritten_query"],
                    "chunk_ids": [doc.chunk_id for doc in docs],
                    "result_count": len(docs),
                },
            )
        ],
    }


def _result_to_doc(result: WebSearchResult, index: int) -> RetrievedDoc:
    chunk_id = f"web_{_slugify(result.url or result.title)}_{index:04d}"
    return RetrievedDoc(
        chunk_id=chunk_id,
        content=result.content,
        metadata={
            "chunk_id": chunk_id,
            "source": f"web:{result.url}",
            "title": result.title,
            "h1": "Web Search",
            "h2": result.title,
            "h3": "",
            "chunk_index": index,
            "has_code": "```" in result.content,
            "char_count": len(result.content),
        },
        score=result.score,
    )


def _slugify(value: str) -> str:
    slug = SLUG_RE.sub("-", value.lower()).strip("-")
    return slug[:80] or "result"
