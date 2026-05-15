import asyncio

from app.core.config import Settings
from app.graph.nodes.common import NodeTimer, trace_entry
from app.graph.state import RAGState
from app.llm.clients import ChatMessage, LLMClient
from app.llm.prompts import GRADING_PROMPT_V1, GradingOutput
from app.schemas.types import GradingResult, RetrievedDoc


async def grader_node(
    state: RAGState,
    llm_client: LLMClient,
    settings: Settings,
) -> dict[str, object]:
    timer = NodeTimer()
    outputs = await asyncio.gather(
        *[
            _grade_doc(state["rewritten_query"], doc, llm_client, settings)
            for doc in state["retrieved_docs"]
        ]
    )
    grading_results = [
        GradingResult(chunk_id=doc.chunk_id, relevant=output.relevant, reasoning=output.reasoning)
        for doc, output in zip(state["retrieved_docs"], outputs, strict=True)
    ]
    relevant_docs = [
        doc for doc, output in zip(state["retrieved_docs"], outputs, strict=True) if output.relevant
    ]
    route_decision = "generate" if relevant_docs else "rewrite"
    if not relevant_docs and state["retry_count"] >= state["max_retries"]:
        route_decision = "fallback"
    return {
        "relevant_docs": relevant_docs,
        "grading_results": grading_results,
        "route_decision": route_decision,
        "trace": [
            trace_entry(
                "grader",
                timer.elapsed_ms(),
                {
                    "relevant_chunk_ids": [doc.chunk_id for doc in relevant_docs],
                    "grading_results": [result.model_dump() for result in grading_results],
                    "route_decision": route_decision,
                },
            )
        ],
    }


async def _grade_doc(
    query: str,
    doc: RetrievedDoc,
    llm_client: LLMClient,
    settings: Settings,
) -> GradingOutput:
    output = await llm_client.complete(
        messages=[
            ChatMessage(role="system", content=GRADING_PROMPT_V1),
            ChatMessage(
                role="user",
                content=f"Question:\n{query}\n\nChunk {doc.chunk_id}:\n{doc.content}",
            ),
        ],
        model=settings.grading_model,
        response_model=GradingOutput,
    )
    return output

