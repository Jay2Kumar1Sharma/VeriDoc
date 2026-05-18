"use client"

import { FileText, Globe2, Trash2 } from "lucide-react"

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
  const isUrl = document.source.startsWith("http")
  const Icon = isUrl ? Globe2 : FileText

  const displaySource = isUrl
    ? (() => {
        try {
          return new URL(document.source).hostname
        } catch {
          return document.source
        }
      })()
    : document.source

  return (
    <article
      className="group rounded-2xl p-4 transition-all duration-200
                 border border-white/55 dark:border-white/[0.08]
                 bg-white/55 dark:bg-white/[0.04]
                 backdrop-blur-xl shadow-sm shadow-black/5 dark:shadow-black/20
                 hover:border-white/70 dark:hover:border-white/[0.14]
                 hover:bg-white/70 dark:hover:bg-white/[0.07]
                 hover:shadow-md"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex min-w-0 gap-3">
          <div
            className={`grid size-10 shrink-0 place-items-center rounded-xl backdrop-blur-sm
                        border border-white/40 dark:border-white/10
                        ${isUrl
                          ? "bg-amber-400/20 dark:bg-amber-500/15 text-amber-600 dark:text-amber-400"
                          : "bg-primary/15 dark:bg-primary/20 text-primary"
                        }`}
          >
            <Icon className="size-5" />
          </div>
          <div className="min-w-0">
            <h3 className="truncate text-sm font-medium leading-snug">{document.title}</h3>
            <p className="mt-0.5 truncate text-xs text-muted-foreground" title={document.source}>
              {displaySource}
            </p>
          </div>
        </div>
        <Button
          size="icon-sm"
          variant="ghost"
          aria-label="Delete document"
          className="shrink-0 opacity-0 transition-opacity group-hover:opacity-100
                     hover:bg-red-500/10 hover:text-red-500"
          onClick={() => onDelete(document.doc_id)}
        >
          <Trash2 className="size-3.5" />
        </Button>
      </div>

      <div className="mt-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Badge variant="secondary" className="text-[10px]">
            {document.chunk_count} chunks
          </Badge>
          <Badge variant="outline" className="text-[10px]">
            {isUrl ? "URL" : "file"}
          </Badge>
        </div>
        <span className="text-xs text-muted-foreground">
          {new Date(document.ingested_at).toLocaleDateString(undefined, {
            month: "short",
            day: "numeric",
            year: "numeric",
          })}
        </span>
      </div>
    </article>
  )
}
