"use client"

import type { Citation } from "@/lib/types"

export function CitationPill({
  citation,
  onClick,
}: {
  citation: Citation
  onClick: (citation: Citation) => void
}) {
  const isWeb = citation.source.startsWith("web:")

  return (
    <button
      type="button"
      aria-label={`Open citation ${citation.chunk_id}`}
      className={`ml-1 inline-flex translate-y-[-0.25em] rounded px-1.5 py-0.5 text-[10px] font-medium ring-1 ${
        isWeb
          ? "bg-amber-500/10 text-amber-600 ring-amber-500/30"
          : "bg-primary/10 text-primary ring-primary/30"
      }`}
      onClick={() => onClick(citation)}
    >
      {citation.chunk_id}
    </button>
  )
}

