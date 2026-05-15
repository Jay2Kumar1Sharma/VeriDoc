from typing import Literal

from pydantic import BaseModel, Field, HttpUrl

from app.schemas.types import Citation


class QueryRequest(BaseModel):
    question: str = Field(min_length=1)
    session_id: str | None = None
    top_k: int = Field(default=5, ge=1, le=20)
    max_retries: int = Field(default=2, ge=0, le=5)


class QueryResponse(BaseModel):
    trace_id: str
    answer: str
    citations: list[Citation]
    query_type: Literal["conceptual", "how-to", "troubleshooting", "api-reference"]
    retries_used: int
    grounded: bool
    latency_ms: int


class IngestUrlsRequest(BaseModel):
    urls: list[HttpUrl] = Field(min_length=1)


class IngestResult(BaseModel):
    source: str
    doc_id: str | None
    chunk_count: int
    status: str
    error: str | None = None


class IngestResponse(BaseModel):
    ingested: list[IngestResult] = Field(default_factory=list)
    failed: list[IngestResult] = Field(default_factory=list)
    job_id: str | None = None
    status: str = "completed"


class IngestJobResponse(BaseModel):
    job_id: str
    status: Literal["queued", "running", "completed", "failed"]
    ingested: list[IngestResult] = Field(default_factory=list)
    failed: list[IngestResult] = Field(default_factory=list)
    error: str | None = None


class DocumentSummary(BaseModel):
    doc_id: str
    source: str
    title: str
    ingested_at: str
    chunk_count: int
    status: str


class DocumentsResponse(BaseModel):
    documents: list[DocumentSummary]
    limit: int
    offset: int


class FeedbackRequest(BaseModel):
    trace_id: str
    rating: Literal[-1, 1]
    comment: str | None = None


class TraceResponse(BaseModel):
    trace_id: str
    question: str
    answer: str
    retries: int
    grounded: bool
    latency_ms: int
    created_at: str
    trace_steps: list[dict[str, object]]


class TracesResponse(BaseModel):
    traces: list[TraceResponse]
    limit: int
    offset: int


class SessionSummary(BaseModel):
    session_id: str
    created_at: str
    preview: str


class SessionMessage(BaseModel):
    id: int
    session_id: str
    role: str
    content: str
    created_at: str


class SessionsResponse(BaseModel):
    sessions: list[SessionSummary]


class SessionMessagesResponse(BaseModel):
    messages: list[SessionMessage]


class HealthResponse(BaseModel):
    status: str
    version: str
    env: str
    vector_store_chunks: int
    llm_provider: str
    embedding_provider: str
