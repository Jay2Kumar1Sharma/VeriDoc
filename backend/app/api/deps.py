from collections.abc import AsyncIterator
from typing import Any, Protocol

from fastapi import Request

from app.core.config import Settings
from app.graph.builder import build_graph
from app.stores.metadata_store import MetadataStore
from app.stores.vector_store import ChromaVectorStore, VectorStore


class GraphRunner(Protocol):
    async def ainvoke(
        self,
        input: Any,
        config: dict[str, Any] | None = None,
    ) -> dict[str, Any]: ...


def get_settings_dep(request: Request) -> Settings:
    return request.app.state.settings


def get_metadata_store(request: Request) -> MetadataStore:
    return request.app.state.metadata_store


def get_vector_store(request: Request) -> VectorStore:
    vector_store = getattr(request.app.state, "vector_store", None)
    if vector_store is None:
        vector_store = ChromaVectorStore(settings=request.app.state.settings)
        request.app.state.vector_store = vector_store
    return vector_store


async def get_graph(request: Request) -> AsyncIterator[GraphRunner]:
    graph = getattr(request.app.state, "graph_runner", None)
    if graph is None:
        vector_store = get_vector_store(request)
        graph = build_graph(vector_store=vector_store, settings=request.app.state.settings)
    yield graph
