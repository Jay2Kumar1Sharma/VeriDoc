"use client"

import { FileText, Trash2 } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import type { DocumentSummary } from "@/lib/types"

export function DocumentCard({
  document,
  onDelete,
}: {
  document: DocumentSummary
  onDelete: (docId: string) => void
}) {
  return (
    <article className="rounded-lg border bg-card p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="flex min-w-0 gap-3">
          <div className="grid size-10 shrink-0 place-items-center rounded-md bg-primary/10 text-primary">
            <FileText className="size-5" />
          </div>
          <div className="min-w-0">
            <h3 className="truncate text-sm font-medium">{document.title}</h3>
            <p className="mt-1 truncate text-xs text-muted-foreground">{document.source}</p>
          </div>
        </div>
        <Button size="icon-sm" variant="ghost" aria-label="Delete document" onClick={() => onDelete(document.doc_id)}>
          <Trash2 className="size-4" />
        </Button>
      </div>
      <div className="mt-4 flex items-center justify-between">
        <Badge variant="secondary">{document.chunk_count} chunks</Badge>
        <span className="text-xs text-muted-foreground">{new Date(document.ingested_at).toLocaleString()}</span>
      </div>
    </article>
  )
}

