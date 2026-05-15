"use client"

import { Command } from "cmdk"
import { FileText, MessageSquare, SearchCode } from "lucide-react"
import { useRouter } from "next/navigation"
import { useEffect, useState } from "react"

export function CommandPalette() {
  const [open, setOpen] = useState(false)
  const router = useRouter()

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault()
        setOpen((value) => !value)
      }
    }
    window.addEventListener("keydown", onKeyDown)
    return () => window.removeEventListener("keydown", onKeyDown)
  }, [])

  if (!open) return null

  const go = (path: string) => {
    setOpen(false)
    router.push(path)
  }

  return (
    <div className="fixed inset-0 z-50 bg-background/80 p-4 backdrop-blur">
      <Command className="mx-auto mt-24 max-w-lg overflow-hidden rounded-lg border bg-popover shadow-2xl">
        <Command.Input
          autoFocus
          className="h-12 w-full border-b bg-transparent px-4 outline-none"
          placeholder="Navigate..."
        />
        <Command.List className="p-2">
          <Command.Empty className="px-3 py-6 text-center text-sm text-muted-foreground">
            No results
          </Command.Empty>
          <Command.Item className="flex cursor-pointer items-center gap-3 rounded-md px-3 py-2 aria-selected:bg-muted" onSelect={() => go("/")}>
            <MessageSquare className="size-4" /> Chat
          </Command.Item>
          <Command.Item className="flex cursor-pointer items-center gap-3 rounded-md px-3 py-2 aria-selected:bg-muted" onSelect={() => go("/documents")}>
            <FileText className="size-4" /> Documents
          </Command.Item>
          <Command.Item className="flex cursor-pointer items-center gap-3 rounded-md px-3 py-2 aria-selected:bg-muted" onSelect={() => go("/traces")}>
            <SearchCode className="size-4" /> Traces
          </Command.Item>
        </Command.List>
      </Command>
    </div>
  )
}

