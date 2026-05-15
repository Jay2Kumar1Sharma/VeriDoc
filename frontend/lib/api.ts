import type {
  DocumentSummary,
  HealthResponse,
  IngestJob,
  QueryResponse,
  TraceResponse,
} from "@/lib/types"

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000"

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  })

  if (!response.ok) {
    const detail = await response.text()
    throw new Error(detail || `Request failed with ${response.status}`)
  }

  if (response.status === 204) {
    return undefined as T
  }

  return (await response.json()) as T
}

export async function getHealth(): Promise<HealthResponse> {
  return request<HealthResponse>("/health")
}

export async function askQuestion(question: string, sessionId?: string): Promise<QueryResponse> {
  return request<QueryResponse>("/query", {
    method: "POST",
    body: JSON.stringify({ question, session_id: sessionId }),
  })
}

export async function getTrace(traceId: string): Promise<TraceResponse> {
  return request<TraceResponse>(`/traces/${traceId}`)
}

export async function listTraces(): Promise<{ traces: TraceResponse[] }> {
  return request<{ traces: TraceResponse[] }>("/traces?limit=50&offset=0")
}

export async function listDocuments(): Promise<{ documents: DocumentSummary[] }> {
  return request<{ documents: DocumentSummary[] }>("/documents?limit=100&offset=0")
}

export async function ingestUrls(urls: string[]): Promise<{ job_id?: string | null }> {
  return request<{ job_id?: string | null }>("/ingest", {
    method: "POST",
    body: JSON.stringify({ urls }),
  })
}

export async function uploadFiles(files: File[]): Promise<{ job_id?: string | null }> {
  const form = new FormData()
  files.forEach((file) => form.append("files", file))
  const response = await fetch(`${API_BASE}/ingest`, {
    method: "POST",
    body: form,
  })
  if (!response.ok) {
    throw new Error(await response.text())
  }
  return (await response.json()) as { job_id?: string | null }
}

export async function getIngestJob(jobId: string): Promise<IngestJob> {
  return request<IngestJob>(`/ingest/jobs/${jobId}`)
}

export async function deleteDocument(docId: string): Promise<void> {
  await request<void>(`/documents/${docId}`, { method: "DELETE" })
}

export async function sendFeedback(
  traceId: string,
  rating: 1 | -1,
  comment?: string,
): Promise<void> {
  await request<void>("/feedback", {
    method: "POST",
    body: JSON.stringify({ trace_id: traceId, rating, comment }),
  })
}

export { API_BASE }

