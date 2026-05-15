from app.core.config import Settings
from app.graph.nodes.common import NodeTimer, trace_entry
from app.graph.state import RAGState
from app.stores.vector_store import VectorStore


async def retrieval_node(
    state: RAGState,
    vector_store: VectorStore,
    settings: Settings,
) -> dict[str, object]:
    timer = NodeTimer()
    docs = vector_store.similarity_search(state["rewritten_query"], k=settings.top_k)
    return {
        "retrieved_docs": docs,
        "trace": [
            trace_entry(
                "retrieval",
                timer.elapsed_ms(),
                {
                    "query": state["rewritten_query"],
                    "chunk_ids": [doc.chunk_id for doc in docs],
                },
            )
        ],
    }

