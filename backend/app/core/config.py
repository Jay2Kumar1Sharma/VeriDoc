from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(default="VeriDoc RAG Assistant", alias="APP_NAME")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    env: str = Field(default="local", alias="ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    anthropic_api_key: str | None = Field(default=None, alias="ANTHROPIC_API_KEY")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    gemini_api_key: str | None = Field(default=None, alias="GEMINI_API_KEY")
    tavily_api_key: str | None = Field(default=None, alias="TAVILY_API_KEY")

    llm_provider: Literal["anthropic", "openai", "gemini"] = Field(
        default="gemini",
        alias="LLM_PROVIDER",
    )
    generation_model: str = Field(default="gemini-2.5-flash-lite", alias="GENERATION_MODEL")
    grading_model: str = Field(default="gemini-2.5-flash-lite", alias="GRADING_MODEL")

    embedding_provider: Literal["openai", "sentence-transformers"] = Field(
        default="sentence-transformers",
        alias="EMBEDDING_PROVIDER",
    )
    embedding_model: str = Field(default="BAAI/bge-small-en-v1.5", alias="EMBEDDING_MODEL")

    chroma_persist_dir: str = Field(default="./chroma_data", alias="CHROMA_PERSIST_DIR")
    sqlite_path: str = Field(default="./app.db", alias="SQLITE_PATH")

    chunk_size: int = Field(default=800, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=150, alias="CHUNK_OVERLAP")
    top_k: int = Field(default=5, alias="TOP_K")
    max_retries: int = Field(default=2, alias="MAX_RETRIES")
    enable_hallucination_check: bool = Field(
        default=True,
        alias="ENABLE_HALLUCINATION_CHECK",
    )
    enable_web_search_fallback: bool = Field(
        default=False,
        alias="ENABLE_WEB_SEARCH_FALLBACK",
    )
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000"],
        alias="CORS_ORIGINS",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
