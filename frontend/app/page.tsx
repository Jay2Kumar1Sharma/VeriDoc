"use client"

import { motion } from "framer-motion"
import { AlertTriangle, MessageSquarePlus } from "lucide-react"
import { useEffect, useState } from "react"

import { AnswerRenderer } from "@/components/AnswerRenderer"
import { ChatInput } from "@/components/ChatInput"
import { CitationDrawer } from "@/components/CitationDrawer"
import { EmptyState } from "@/components/EmptyState"
import { FeedbackButtons } from "@/components/FeedbackButtons"
import { TraceTimeline } from "@/components/TraceTimeline"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { useChat } from "@/hooks/useChat"
import { useSessionMessages, useSessions } from "@/hooks/useSessions"
import type { ChatMessage, Citation } from "@/lib/types"

export default function Home() {
  const [sessionId, setSessionId] = useState(() => crypto.randomUUID())
  const { messages, send, isLoading, loadHistory, clear } = useChat(sessionId)
  const sessions = useSessions()
  const history = useSessionMessages(sessionId)
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

  useEffect(() => {
    if (!history.data) return
    const loaded: ChatMessage[] = history.data.messages.map((message) => ({
      id: String(message.id),
      role: message.role,
      content: message.content,
    }))
    loadHistory(loaded)
  }, [history.data, loadHistory])

  const newChat = () => {
    setSessionId(crypto.randomUUID())
    clear()
  }

  const submit = (value = input) => {
    if (!value.trim()) return
    setInput("")
    send(value)
  }

  return (
    <div className="mx-auto grid min-h-[calc(100vh-7rem)] max-w-7xl grid-cols-1 gap-6 px-4 py-6 lg:grid-cols-[260px_1fr]">
      <aside className="hidden border-r pr-4 lg:block">
        <Button className="mb-4 w-full justify-start" variant="outline" onClick={newChat}>
          <MessageSquarePlus className="mr-2 size-4" />
          New chat
        </Button>
        <div className="space-y-2">
          {(sessions.data?.sessions ?? []).map((session) => (
            <button
              key={session.session_id}
              type="button"
              onClick={() => setSessionId(session.session_id)}
              className={`w-full rounded-md px-3 py-2 text-left text-sm transition hover:bg-muted ${
                session.session_id === sessionId ? "bg-muted text-foreground" : "text-muted-foreground"
              }`}
            >
              <span className="line-clamp-2">{session.preview}</span>
            </button>
          ))}
        </div>
      </aside>
      <section className="flex min-w-0 flex-col">
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
      </section>
      <div className="fixed inset-x-0 bottom-0 border-t bg-background/90 p-4 backdrop-blur">
        <div className="mx-auto max-w-3xl">
          <ChatInput value={input} onChange={setInput} onSubmit={() => submit()} disabled={isLoading} />
        </div>
      </div>
      <CitationDrawer citation={citation} open={Boolean(citation)} onOpenChange={(open) => !open && setCitation(null)} />
    </div>
  )
}
