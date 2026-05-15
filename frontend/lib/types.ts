export type Citation = {
  chunk_id: string
  source: string
  title: string
  snippet: string
  header_path: string[]
}

export type QueryResponse = {
  trace_id: string
  answer: string
  citations: Citation[]
  query_type: "conceptual" | "how-to" | "troubleshooting" | "api-reference"
  retries_used: number
  grounded: boolean
  latency_ms: number
}

export type TraceStep = {
  node: string
  duration_ms?: number
  output?: Record<string, unknown>
}

export type TraceResponse = {
  trace_id: string
  question: string
  answer: string
  retries: number
  grounded: boolean
  latency_ms: number
  created_at: string
  trace_steps: TraceStep[]
}

export type SessionSummary = {
  session_id: string
  created_at: string
  preview: string
}

export type SessionMessage = {
  id: number
  session_id: string
  role: "user" | "assistant"
  content: string
  created_at: string
}

export type DocumentSummary = {
  doc_id: string
  source: string
  title: string
  ingested_at: string
  chunk_count: number
  status: string
}

export type IngestJob = {
  job_id: string
  status: "queued" | "running" | "completed" | "failed"
  ingested: IngestResult[]
  failed: IngestResult[]
  error?: string | null
}

export type IngestResult = {
  source: string
  doc_id: string | null
  chunk_count: number
  status: string
  error?: string | null
}

export type HealthResponse = {
  status: string
  version: string
  env: string
  vector_store_chunks: number
  llm_provider: string
  embedding_provider: string
}

export type ChatMessage = {
  id: string
  role: "user" | "assistant"
  content: string
  response?: QueryResponse
  trace?: TraceResponse | null
}
