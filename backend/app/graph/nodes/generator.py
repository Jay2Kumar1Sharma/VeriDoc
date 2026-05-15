import re

from app.core.config import Settings
from app.graph.nodes.common import NodeTimer, trace_entry
from app.graph.state import RAGState
from app.llm.clients import ChatMessage, LLMClient
from app.llm.prompts import GENERATION_PROMPT_V1
from app.schemas.types import Citation, RetrievedDoc

CITATION_RE = re.compile(r"\[#([A-Za-z0-9_.:-]+)\]")


async def generator_node(
    state: RAGState,
    llm_client: LLMClient,
    settings: Settings,
) -> dict[str, object]:
    timer = NodeTimer()
    context = build_context(state["relevant_docs"])
    answer = await llm_client.complete(
        messages=[
            ChatMessage(role="system", content=GENERATION_PROMPT_V1),
            ChatMessage(
                role="user",
                content=f"Question:\n{state['original_query']}\n\nContext:\n{context}",
            ),
        ],
        model=settings.generation_model,
        response_model=None,
    )
    citations = extract_citations(answer, state["relevant_docs"])
    return {
        "answer": answer,
        "citations": citations,
        "trace": [
            trace_entry(
                "generator",
                timer.elapsed_ms(),
                {
                    "citation_chunk_ids": [citation.chunk_id for citation in citations],
                    "answer_chars": len(answer),
                },
            )
        ],
    }


def build_context(docs: list[RetrievedDoc]) -> str:
    blocks: list[str] = []
    for doc in docs:
        header_path = _header_path(doc)
        blocks.append(
            f"[#{doc.chunk_id}]\n"
            f"Title: {doc.metadata.get('title', '')}\n"
            f"Source: {doc.metadata.get('source', '')}\n"
            f"Headers: {' > '.join(header_path)}\n"
            f"Content:\n{doc.content}"
        )
    return "\n\n---\n\n".join(blocks)


def extract_citations(answer: str, docs: list[RetrievedDoc]) -> list[Citation]:
    docs_by_id = {doc.chunk_id: doc for doc in docs}
    citations: list[Citation] = []
    seen: set[str] = set()
    for chunk_id in CITATION_RE.findall(answer):
        if chunk_id in seen or chunk_id not in docs_by_id:
            continue
        seen.add(chunk_id)
        doc = docs_by_id[chunk_id]
        citations.append(
            Citation(
                chunk_id=chunk_id,
                source=str(doc.metadata.get("source", "")),
                title=str(doc.metadata.get("title", "")),
                snippet=doc.content[:300],
                header_path=_header_path(doc),
            )
        )
    return citations


def _header_path(doc: RetrievedDoc) -> list[str]:
    return [
        str(value)
        for value in [doc.metadata.get("h1"), doc.metadata.get("h2"), doc.metadata.get("h3")]
        if value
    ]

