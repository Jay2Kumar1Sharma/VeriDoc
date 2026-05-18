"use client"

import { Send } from "lucide-react"
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
    <form
      onSubmit={submit}
      className="overflow-hidden rounded-2xl shadow-xl shadow-black/10 dark:shadow-black/30
                 border border-white/60 dark:border-white/[0.10]
                 bg-white/70 dark:bg-white/[0.07]
                 backdrop-blur-2xl saturate-150
                 transition-all duration-200
                 focus-within:border-primary/40 dark:focus-within:border-primary/30
                 focus-within:shadow-[0_8px_40px_-8px_hsl(var(--primary)/0.25)]"
    >
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
        placeholder="Ask anything about the docs…"
        className="max-h-48 min-h-[3.25rem] w-full resize-none bg-transparent px-4 pt-4 pb-2 text-sm outline-none
                   placeholder:text-muted-foreground/50 disabled:opacity-40"
      />
      <div className="flex items-center justify-between px-3 pb-3 pt-1">
        <span className="select-none text-[10px] text-muted-foreground/40">
          <kbd className="rounded border border-border/40 px-1 py-px font-mono text-[9px]">Ctrl</kbd>
          {" + "}
          <kbd className="rounded border border-border/40 px-1 py-px font-mono text-[9px]">↵</kbd>
        </span>
        {disabled ? (
          <div className="flex items-center gap-1 py-1 pr-0.5">
            <span className="size-1.5 animate-bounce rounded-full bg-primary [animation-delay:-0.3s]" />
            <span className="size-1.5 animate-bounce rounded-full bg-primary [animation-delay:-0.15s]" />
            <span className="size-1.5 animate-bounce rounded-full bg-primary" />
          </div>
        ) : (
          <Button
            type="submit"
            size="icon"
            className="size-8 rounded-xl"
            disabled={!value.trim()}
            aria-label="Send"
          >
            <Send className="size-3.5" />
          </Button>
        )}
      </div>
    </form>
  )
}
