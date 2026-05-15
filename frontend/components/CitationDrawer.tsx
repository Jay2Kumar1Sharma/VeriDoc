"use client"

import { ExternalLink } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import type { Citation } from "@/lib/types"

export function CitationDrawer({
  citation,
  open,
  onOpenChange,
}: {
  citation: Citation | null
  open: boolean
  onOpenChange: (open: boolean) => void
}) {
  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="w-full overflow-y-auto sm:max-w-xl">
        <SheetHeader>
          <SheetTitle>{citation?.title ?? "Citation"}</SheetTitle>
          <SheetDescription>{citation?.chunk_id}</SheetDescription>
        </SheetHeader>
        {citation ? (
          <div className="mt-6 space-y-5">
            <div className="flex flex-wrap gap-2">
              {citation.header_path.map((part) => (
                <Badge key={part} variant="secondary">
                  {part}
                </Badge>
              ))}
            </div>
            <pre className="whitespace-pre-wrap rounded-lg border bg-muted/40 p-4 text-sm leading-6">
              {citation.snippet}
            </pre>
            <a
              href={citation.source.replace(/^web:/, "")}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-2 text-sm text-primary hover:underline"
            >
              Open source <ExternalLink className="size-3.5" />
            </a>
          </div>
        ) : null}
      </SheetContent>
    </Sheet>
  )
}

