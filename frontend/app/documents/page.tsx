"use client"

import { Search } from "lucide-react"
import { useMemo, useState } from "react"

import { DocumentCard } from "@/components/DocumentCard"
import { IngestDialog } from "@/components/IngestDialog"
import { CardGridSkeleton } from "@/components/SkeletonLoaders"
import { Input } from "@/components/ui/input"
import { useDocuments } from "@/hooks/useDocuments"

export default function DocumentsPage() {
  const [filter, setFilter] = useState("")
  const { documents, remove } = useDocuments()
  const filtered = useMemo(
    () =>
      documents.data?.documents.filter((document) =>
        `${document.title} ${document.source}`.toLowerCase().includes(filter.toLowerCase()),
      ) ?? [],
    [documents.data, filter],
  )

  return (
    <div className="mx-auto max-w-7xl px-4 py-8">
      <div className="mb-6 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Documents</h1>
          <p className="mt-1 text-sm text-muted-foreground">Indexed sources available to the RAG graph</p>
        </div>
        <IngestDialog />
      </div>
      <div className="mb-6 flex items-center gap-2 rounded-lg border bg-card px-3">
        <Search className="size-4 text-muted-foreground" />
        <Input
          value={filter}
          onChange={(event) => setFilter(event.target.value)}
          placeholder="Filter sources"
          className="border-0 bg-transparent shadow-none focus-visible:ring-0"
        />
      </div>
      {documents.isLoading ? (
        <CardGridSkeleton />
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {filtered.map((document) => (
            <DocumentCard
              key={document.doc_id}
              document={document}
              onDelete={(docId) => {
                if (window.confirm("Delete this document and its chunks?")) {
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

