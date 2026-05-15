from collections.abc import Sequence
from importlib import import_module
from typing import Any, Protocol, cast

from app.core.config import Settings, get_settings


class EmbeddingProvider(Protocol):
    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]: ...

    def embed_query(self, text: str) -> list[float]: ...


class OpenAIEmbedder:
    def __init__(self, api_key: str, model: str = "text-embedding-3-small") -> None:
        openai_module = import_module("openai")
        client_cls = openai_module.OpenAI
        self._client = client_cls(api_key=api_key)
        self._model = model

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        response = self._client.embeddings.create(model=self._model, input=list(texts))
        return [list(item.embedding) for item in response.data]

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]


class SentenceTransformersEmbedder:
    def __init__(self, model: str = "BAAI/bge-small-en-v1.5") -> None:
        sentence_transformers = import_module("sentence_transformers")
        model_cls = sentence_transformers.SentenceTransformer
        self._model = model_cls(model)

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        vectors = self._model.encode(
            list(texts),
            normalize_embeddings=True,
            convert_to_numpy=False,
            show_progress_bar=False,
        )
        return [list(map(float, vector)) for vector in cast(Any, vectors)]

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]


def get_embedder(settings: Settings | None = None) -> EmbeddingProvider:
    resolved_settings = settings or get_settings()
    if resolved_settings.embedding_provider == "openai":
        if not resolved_settings.openai_api_key:
            msg = "OPENAI_API_KEY is required when EMBEDDING_PROVIDER=openai"
            raise ValueError(msg)
        return OpenAIEmbedder(
            api_key=resolved_settings.openai_api_key,
            model=resolved_settings.embedding_model,
        )
    return SentenceTransformersEmbedder(model=resolved_settings.embedding_model)

