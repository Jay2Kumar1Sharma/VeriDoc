from app.core.config import Settings
from app.graph.nodes.common import NodeTimer, trace_entry
from app.graph.state import RAGState
from app.llm.clients import ChatMessage, LLMClient
from app.llm.prompts import QUERY_ANALYSIS_PROMPT_V1, QueryAnalysisOutput


async def query_analysis_node(
    state: RAGState,
    llm_client: LLMClient,
    settings: Settings,
) -> dict[str, object]:
    timer = NodeTimer()
    user_prompt = state["original_query"]
    if state["conversation_context"]:
        user_prompt = (
            "Conversation context:\n"
            f"{state['conversation_context']}\n\n"
            f"Current question:\n{state['original_query']}"
        )
    output = await llm_client.complete(
        messages=[
            ChatMessage(role="system", content=QUERY_ANALYSIS_PROMPT_V1),
            ChatMessage(role="user", content=user_prompt),
        ],
        model=settings.grading_model,
        response_model=QueryAnalysisOutput,
    )
    return {
        "rewritten_query": output.rewritten_query,
        "query_type": output.query_type,
        "trace": [
            trace_entry(
                "query_analysis",
                timer.elapsed_ms(),
                output.model_dump(),
            )
        ],
    }
