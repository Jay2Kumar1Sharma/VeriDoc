"use client"

import { motion } from "framer-motion"
import { AlertTriangle } from "lucide-react"
import { useEffect, useState } from "react"

import { AnswerRenderer } from "@/components/AnswerRenderer"
import { ChatInput } from "@/components/ChatInput"
import { CitationDrawer } from "@/components/CitationDrawer"
import { EmptyState } from "@/components/EmptyState"
import { FeedbackButtons } from "@/components/FeedbackButtons"
import { TraceTimeline } from "@/components/TraceTimeline"
import { Badge } from "@/components/ui/badge"
import { useChat } from "@/hooks/useChat"
import type { Citation } from "@/lib/types"

export default function Home() {
  const { messages, send, isLoading } = useChat()
  const [input, setInput] = useState("")
  const [citation, setCitation] = useState<Citation | null>(null)

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "/" && document.activeElement?.tagName !== "TEXTAREA") {
        event.preventDefault()
        document.querySelector<HTMLTextAreaElement>("textarea")?.focus()
      }
    }
    window.addEventListener("keydown", onKeyDown)
    return () => window.removeEventListener("keydown", onKeyDown)
  }, [])

  const submit = (value = input) => {
    if (!value.trim()) return
    setInput("")
    send(value)
  }

  return (
    <div className="mx-auto flex min-h-[calc(100vh-7rem)] max-w-5xl flex-col px-4 py-6">
      {!messages.length ? <EmptyState onExample={submit} /> : null}
      <div className="flex-1 space-y-6 pb-28">
        {messages.map((message) => (
          <motion.article
            key={message.id}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className={message.role === "user" ? "flex justify-end" : "flex justify-start"}
          >
            <div
              className={
                message.role === "user"
                  ? "max-w-[70%] rounded-lg bg-primary px-4 py-3 text-sm text-primary-foreground"
                  : "w-full rounded-lg border bg-card p-4"
              }
            >
              {message.role === "user" ? (
                message.content
              ) : (
                <div>
                  {message.response && !message.response.grounded ? (
                    <div className="mb-3 flex items-center gap-2 rounded-md border border-amber-500/30 bg-amber-500/10 px-3 py-2 text-sm text-amber-700 dark:text-amber-300">
                      <AlertTriangle className="size-4" />
                      This answer may not be fully supported by the source docs
                    </div>
                  ) : null}
                  {message.content ? (
                    <AnswerRenderer
                      content={message.content}
                      citations={message.response?.citations ?? []}
                      onCitationClick={setCitation}
                    />
                  ) : (
                    <div className="h-5 w-48 animate-pulse rounded bg-muted" />
                  )}
                  {message.response ? (
                    <div className="mt-4 flex flex-wrap items-center gap-2">
                      <Badge variant="secondary">{message.response.query_type}</Badge>
                      <Badge variant="secondary">{message.response.retries_used} retries</Badge>
                      <Badge variant={message.response.grounded ? "secondary" : "destructive"}>
                        {message.response.grounded ? "grounded" : "ungrounded"}
                      </Badge>
                    </div>
                  ) : null}
                  {message.trace ? (
                    <details className="mt-4">
                      <summary className="cursor-pointer text-sm font-medium">Trace</summary>
                      <div className="mt-3">
                        <TraceTimeline steps={message.trace.trace_steps} />
                      </div>
                    </details>
                  ) : null}
                  {message.response ? <FeedbackButtons traceId={message.response.trace_id} /> : null}
                </div>
              )}
            </div>
          </motion.article>
        ))}
      </div>
      <div className="fixed inset-x-0 bottom-0 border-t bg-background/90 p-4 backdrop-blur">
        <div className="mx-auto max-w-3xl">
          <ChatInput value={input} onChange={setInput} onSubmit={() => submit()} disabled={isLoading} />
        </div>
      </div>
      <CitationDrawer citation={citation} open={Boolean(citation)} onOpenChange={(open) => !open && setCitation(null)} />
    </div>
  )
}
