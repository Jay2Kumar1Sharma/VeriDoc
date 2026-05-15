from app.core.config import Settings
from app.graph.nodes.common import NodeTimer, trace_entry
from app.graph.state import RAGState
from app.llm.clients import ChatMessage, LLMClient
from app.llm.prompts import REWRITE_PROMPT_V1, RewriteOutput


async def rewriter_node(
    state: RAGState,
    llm_client: LLMClient,
    settings: Settings,
) -> dict[str, object]:
    timer = NodeTimer()
    feedback = "\n".join(
        f"{result.chunk_id}: {result.reasoning}" for result in state["grading_results"]
    )
    output = await llm_client.complete(
        messages=[
            ChatMessage(role="system", content=REWRITE_PROMPT_V1),
            ChatMessage(
                role="user",
                content=(
                    f"Original question:\n{state['original_query']}\n\n"
                    f"Previous rewrite:\n{state['rewritten_query']}\n\n"
                    f"Grader feedback:\n{feedback or 'No relevant documents found.'}"
                ),
            ),
        ],
        model=settings.grading_model,
        response_model=RewriteOutput,
    )
    retry_count = min(state["retry_count"] + 1, state["max_retries"])
    return {
        "rewritten_query": output.rewritten_query,
        "retry_count": retry_count,
        "trace": [
            trace_entry(
                "rewriter",
                timer.elapsed_ms(),
                {
                    "rewritten_query": output.rewritten_query,
                    "reasoning": output.reasoning,
                    "retry_count": retry_count,
                },
            )
        ],
    }

