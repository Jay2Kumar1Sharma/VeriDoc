import os
from collections.abc import Sequence
from importlib import import_module
from typing import Any, Protocol

from app.core.config import Settings, get_settings
from app.ingestion.chunker import Chunk
from app.llm.embeddings import EmbeddingProvider, get_embedder
from app.schemas.types import RetrievedDoc


class VectorStore(Protocol):
    def add_chunks(self, chunks: Sequence[Chunk]) -> None: ...

    def similarity_search(
        self,
        query: str,
        k: int,
        filter: dict[str, Any] | None = None,
    ) -> list[RetrievedDoc]: ...

    def delete_by_source(self, source: str) -> None: ...

    def count(self) -> int: ...


class ChromaVectorStore:
    def __init__(
        self,
        persist_dir: str | None = None,
        embedder: EmbeddingProvider | None = None,
        collection_name: str = "docs",
        settings: Settings | None = None,
    ) -> None:
        resolved_settings = settings or get_settings()
        os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")
        chromadb = import_module("chromadb")
        chroma_config = import_module("chromadb.config")
        self._client = chromadb.PersistentClient(
            path=persist_dir or resolved_settings.chroma_persist_dir,
            settings=chroma_config.Settings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(name=collection_name)
        self._embedder = embedder or get_embedder(resolved_settings)

    def add_chunks(self, chunks: Sequence[Chunk]) -> None:
        if not chunks:
            return
        documents = [chunk.content for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]
        ids = [str(chunk.metadata["chunk_id"]) for chunk in chunks]
        embeddings = self._embedder.embed_documents(documents)
        self._collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )

    def similarity_search(
        self,
        query: str,
        k: int,
        filter: dict[str, Any] | None = None,
    ) -> list[RetrievedDoc]:
        query_embedding = self._embedder.embed_query(query)
        result = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where=filter,
            include=["documents", "metadatas", "distances"],
        )
        ids = result.get("ids", [[]])[0]
        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]
        docs: list[RetrievedDoc] = []
        for chunk_id, content, metadata, distance in zip(
            ids,
            documents,
            metadatas,
            distances,
            strict=False,
        ):
            docs.append(
                RetrievedDoc(
                    chunk_id=str(chunk_id),
                    content=str(content),
                    metadata=dict(metadata or {}),
                    score=max(0.0, 1.0 - float(distance)),
                )
            )
        return docs

    def delete_by_source(self, source: str) -> None:
        existing = self._collection.get(where={"source": source})
        ids = existing.get("ids", [])
        if ids:
            self._collection.delete(ids=ids)

    def count(self) -> int:
        return int(self._collection.count())
