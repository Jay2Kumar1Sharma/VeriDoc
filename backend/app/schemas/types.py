from typing import Any

from pydantic import BaseModel, Field


class RetrievedDoc(BaseModel):
    chunk_id: str
    content: str
    metadata: dict[str, Any]
    score: float


class GradingResult(BaseModel):
    chunk_id: str
    relevant: bool
    reasoning: str


class Citation(BaseModel):
    chunk_id: str
    source: str
    title: str
    snippet: str
    header_path: list[str] = Field(default_factory=list)

