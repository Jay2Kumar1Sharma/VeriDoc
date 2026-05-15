from app.core.config import Settings
from app.graph.nodes.common import NodeTimer, trace_entry
from app.graph.nodes.generator import build_context
from app.graph.state import RAGState
from app.llm.clients import ChatMessage, LLMClient
from app.llm.prompts import GROUNDEDNESS_PROMPT_V1, GroundednessOutput


async def hallucination_check_node(
    state: RAGState,
    llm_client: LLMClient,
    settings: Settings,
) -> dict[str, object]:
    timer = NodeTimer()
    if not settings.enable_hallucination_check:
        output = GroundednessOutput(grounded=True, unsupported_claims=[])
    else:
        output = await llm_client.complete(
            messages=[
                ChatMessage(role="system", content=GROUNDEDNESS_PROMPT_V1),
                ChatMessage(
                    role="user",
                    content=(
                        f"Answer:\n{state['answer']}\n\n"
                        f"Documentation chunks:\n{build_context(state['relevant_docs'])}"
                    ),
                ),
            ],
            model=settings.grading_model,
            response_model=GroundednessOutput,
        )
    payload = output.model_dump()
    return {
        "hallucination_check": payload,
        "trace": [trace_entry("hallucination_check", timer.elapsed_ms(), payload)],
    }

