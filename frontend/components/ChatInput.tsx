"use client"

import { FileText, Send } from "lucide-react"
import { FormEvent, KeyboardEvent, useRef } from "react"

import { Button } from "@/components/ui/button"

export function ChatInput({
  value,
  onChange,
  onSubmit,
  disabled,
}: {
  value: string
  onChange: (value: string) => void
  onSubmit: () => void
  disabled?: boolean
}) {
  const ref = useRef<HTMLTextAreaElement>(null)

  const submit = (event?: FormEvent) => {
    event?.preventDefault()
    if (value.trim()) onSubmit()
  }

  const onKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
      submit()
    }
  }

  return (
    <form onSubmit={submit} className="rounded-xl border bg-card p-2 shadow-lg">
      <div className="flex items-end gap-2">
        <FileText className="mb-2 size-4 shrink-0 text-muted-foreground" />
        <textarea
          ref={ref}
          aria-label="Ask a question"
          rows={1}
          value={value}
          disabled={disabled}
          onKeyDown={onKeyDown}
          onChange={(event) => {
            onChange(event.target.value)
            event.currentTarget.style.height = "auto"
            event.currentTarget.style.height = `${event.currentTarget.scrollHeight}px`
          }}
          placeholder="Ask anything about the docs..."
          className="max-h-40 min-h-10 flex-1 resize-none bg-transparent py-2 text-sm outline-none"
        />
        <Button type="submit" size="icon-lg" disabled={disabled || !value.trim()} aria-label="Send">
          <Send className="size-4" />
        </Button>
      </div>
    </form>
  )
}

