from app.graph.nodes.common import NodeTimer, trace_entry
from app.graph.state import RAGState

FALLBACK_ANSWER = (
    "I don't have enough information in the indexed documentation to answer this confidently."
)


async def fallback_node(state: RAGState) -> dict[str, object]:
    timer = NodeTimer()
    return {
        "answer": FALLBACK_ANSWER,
        "citations": [],
        "trace": [
            trace_entry(
                "fallback",
                timer.elapsed_ms(),
                {"reason": "no_relevant_docs", "retry_count": state["retry_count"]},
            )
        ],
    }
