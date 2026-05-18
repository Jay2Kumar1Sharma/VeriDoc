"use client"

import { FileText, Layers, Search } from "lucide-react"
import { useMemo, useState } from "react"

import { DocumentCard } from "@/components/DocumentCard"
import { IngestDialog } from "@/components/IngestDialog"
import { CardGridSkeleton } from "@/components/SkeletonLoaders"
import { Input } from "@/components/ui/input"
import { useDocuments } from "@/hooks/useDocuments"

export default function DocumentsPage() {
  const [filter, setFilter] = useState("")
  const { documents, remove } = useDocuments()

  const allDocs = useMemo(() => documents.data?.documents ?? [], [documents.data?.documents])
  const filtered = useMemo(
    () =>
      allDocs.filter((document) =>
        `${document.title} ${document.source}`.toLowerCase().includes(filter.toLowerCase()),
      ),
    [allDocs, filter],
  )

  const totalChunks = allDocs.reduce((sum, doc) => sum + doc.chunk_count, 0)

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 md:px-8">
      {/* Header */}
      <div className="mb-6 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Documents</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Indexed sources available to the RAG pipeline
          </p>
        </div>
        <IngestDialog />
      </div>

      {/* Stats — glass cards */}
      {!documents.isLoading && allDocs.length > 0 && (
        <div className="mb-6 grid grid-cols-2 gap-4">
          {[
            { icon: FileText, value: allDocs.length, label: "Documents" },
            { icon: Layers, value: totalChunks.toLocaleString(), label: "Total chunks" },
          ].map(({ icon: Icon, value, label }) => (
            <div
              key={label}
              className="flex items-center gap-3 rounded-2xl px-4 py-3
                         border border-white/55 dark:border-white/[0.08]
                         bg-white/55 dark:bg-white/[0.04]
                         backdrop-blur-xl shadow-sm shadow-black/5"
            >
              <div className="grid size-9 place-items-center rounded-xl
                              border border-white/40 dark:border-white/10
                              bg-primary/10 dark:bg-primary/15">
                <Icon className="size-4 text-primary" />
              </div>
              <div>
                <p className="text-lg font-semibold leading-none">{value}</p>
                <p className="mt-0.5 text-xs text-muted-foreground">{label}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Search bar — glass */}
      <div className="mb-6 flex items-center gap-2 rounded-xl px-3
                      border border-white/55 dark:border-white/[0.08]
                      bg-white/55 dark:bg-white/[0.04]
                      backdrop-blur-xl
                      focus-within:border-primary/30 dark:focus-within:border-primary/20
                      transition-colors">
        <Search className="size-4 shrink-0 text-muted-foreground" />
        <Input
          value={filter}
          onChange={(event) => setFilter(event.target.value)}
          placeholder="Filter by title or source…"
          className="border-0 bg-transparent shadow-none focus-visible:ring-0"
        />
      </div>

      {/* Document grid */}
      {documents.isLoading ? (
        <CardGridSkeleton />
      ) : filtered.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-2xl py-16 text-center
                        border border-dashed border-white/50 dark:border-white/[0.08]
                        bg-white/30 dark:bg-white/[0.02]
                        backdrop-blur-lg">
          <div className="mb-3 grid size-12 place-items-center rounded-xl bg-muted/60">
            <FileText className="size-6 text-muted-foreground" />
          </div>
          <p className="text-sm font-medium">
            {filter ? "No documents match your search" : "No documents indexed yet"}
          </p>
          <p className="mt-1 text-xs text-muted-foreground">
            {filter ? "Try a different search term" : 'Click "Ingest new" to add your first document'}
          </p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {filtered.map((document) => (
            <DocumentCard
              key={document.doc_id}
              document={document}
              onDelete={(docId) => {
                if (window.confirm("Delete this document and all its chunks?")) {
                  remove.mutate(docId)
                }
              }}
            />
          ))}
        </div>
      )}
    </div>
  )
}
