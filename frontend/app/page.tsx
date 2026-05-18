"use client"

import { motion } from "framer-motion"
import { AlertTriangle, MessageSquare, MessageSquarePlus, PanelLeft } from "lucide-react"
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
  const [historySessionId, setHistorySessionId] = useState<string | null>(null)
  const { messages, send, isLoading, loadHistory, clear } = useChat(sessionId)
  const sessions = useSessions()
  const history = useSessionMessages(historySessionId)
  const [input, setInput] = useState("")
  const [citation, setCitation] = useState<Citation | null>(null)
  const [sidebarOpen, setSidebarOpen] = useState(true)

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
    setHistorySessionId(null)
    clear()
  }

  const loadSession = (selectedSessionId: string) => {
    setSessionId(selectedSessionId)
    setHistorySessionId(selectedSessionId)
  }

  const submit = (value = input) => {
    if (!value.trim()) return
    setInput("")
    send(value)
  }

  const sessionList = sessions.data?.sessions ?? []

  return (
    <div className="flex h-[calc(100vh-3.5rem)] overflow-hidden">

      {/* ── Sidebar ────────────────────────────────────────────────────── */}
      {/* overflow-hidden + transition-[width] lets it slide in/out cleanly */}
      <aside
        className={`
          hidden lg:flex shrink-0 flex-col
          overflow-hidden
          transition-[width] duration-300 ease-in-out
          border-r border-white/50 dark:border-white/[0.07]
          bg-white/35 dark:bg-white/[0.03]
          backdrop-blur-xl
          ${sidebarOpen ? "w-[220px]" : "w-0 border-r-0"}
        `}
      >
        {/* Inner wrapper keeps content at fixed width during animation */}
        <div className="flex h-full w-[220px] flex-col">
          {/* Sidebar header */}
          <div className="shrink-0 border-b border-white/40 dark:border-white/[0.06] p-3 space-y-2">
            {/* Row 1: close button, right-aligned */}
            <div className="flex justify-end">
              <Button
                size="icon-sm"
                variant="ghost"
                aria-label="Hide sidebar"
                onClick={() => setSidebarOpen(false)}
                className="text-muted-foreground hover:text-foreground"
              >
                <PanelLeft className="size-4" />
              </Button>
            </div>
            {/* Row 2: new chat, full width */}
            <Button
              className="w-full justify-start gap-2 text-sm"
              variant="outline"
              onClick={newChat}
            >
              <MessageSquarePlus className="size-3.5" />
              New chat
            </Button>
          </div>

          {/* Session list — starts cleanly below the header */}
          <div className="relative flex-1 overflow-hidden">
            {sessionList.length > 0 && (
              <div className="pointer-events-none absolute inset-x-0 bottom-0 z-10 h-10 bg-gradient-to-t from-background/60 to-transparent" />
            )}
            <div className="h-full overflow-y-auto px-2 pt-2 pb-8">
              {sessionList.length > 0 && (
                <p className="mb-1 px-2 py-1 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground/60">
                  Recent
                </p>
              )}
              {sessionList.map((session) => {
                const active = session.session_id === sessionId
                return (
                  <button
                    key={session.session_id}
                    type="button"
                    onClick={() => loadSession(session.session_id)}
                    className={`group flex w-full items-start gap-2 rounded-lg px-2.5 py-2 text-left transition-colors ${
                      active
                        ? "bg-white/50 dark:bg-white/[0.08] text-primary ring-1 ring-primary/20"
                        : "text-muted-foreground hover:bg-white/40 dark:hover:bg-white/[0.05] hover:text-foreground"
                    }`}
                  >
                    <MessageSquare
                      className={`mt-0.5 size-3 shrink-0 transition-colors ${
                        active ? "text-primary/70" : "text-muted-foreground/40"
                      }`}
                    />
                    <span className="line-clamp-2 text-xs leading-snug">{session.preview}</span>
                  </button>
                )
              })}
            </div>
          </div>
        </div>
      </aside>

      {/* ── Main content ───────────────────────────────────────────────── */}
      <div className="flex min-w-0 flex-1 flex-col">

        {/* Scrollable messages area */}
        <div className="flex-1 overflow-y-auto">
          <div className="mx-auto max-w-3xl px-4 py-4 md:px-8">

            {/* Open-sidebar button — only visible on desktop when sidebar is closed */}
            {!sidebarOpen && (
              <div className="mb-4 hidden lg:flex">
                <Button
                  size="icon-sm"
                  variant="ghost"
                  aria-label="Show sidebar"
                  onClick={() => setSidebarOpen(true)}
                  className="text-muted-foreground hover:text-foreground"
                >
                  <PanelLeft className="size-4" />
                </Button>
              </div>
            )}

            {!messages.length ? <EmptyState onExample={submit} /> : null}

            <div className="space-y-10 pb-6">
              {messages.map((message) => (
                <motion.article
                  key={message.id}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.22, ease: "easeOut" }}
                >
                  {message.role === "user" ? (
                    <div className="flex justify-end">
                      <div className="max-w-[72%] rounded-2xl rounded-tr-md bg-primary px-4 py-3 text-sm text-primary-foreground shadow-sm shadow-primary/20">
                        {message.content}
                      </div>
                    </div>
                  ) : (
                    <div className="flex gap-3.5">
                      <div className="mt-0.5 flex size-7 shrink-0 items-center justify-center rounded-full border bg-card shadow-sm ring-1 ring-primary/10">
                        <svg
                          viewBox="0 0 24 24"
                          fill="none"
                          className="size-3.5 text-primary"
                          stroke="currentColor"
                          strokeWidth="2.5"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        >
                          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                          <path d="m9 12 2 2 4-4" />
                        </svg>
                      </div>

                      <div className="min-w-0 flex-1 space-y-3">
                        {message.response && !message.response.grounded ? (
                          <div className="flex items-start gap-2 rounded-lg border border-amber-500/25 bg-amber-500/8 px-3 py-2.5 text-xs leading-relaxed text-amber-700 dark:text-amber-400">
                            <AlertTriangle className="mt-px size-3.5 shrink-0" />
                            This answer may not be fully supported by the source documents.
                          </div>
                        ) : null}

                        {message.content ? (
                          <AnswerRenderer
                            content={message.content}
                            citations={message.response?.citations ?? []}
                            onCitationClick={setCitation}
                          />
                        ) : (
                          <div className="flex items-center gap-1.5 py-2">
                            <span className="size-1.5 animate-bounce rounded-full bg-primary [animation-delay:-0.3s]" />
                            <span className="size-1.5 animate-bounce rounded-full bg-primary [animation-delay:-0.15s]" />
                            <span className="size-1.5 animate-bounce rounded-full bg-primary" />
                          </div>
                        )}

                        {message.response ? (
                          <div className="flex flex-wrap items-center gap-1.5 pt-1">
                            <Badge variant="secondary" className="text-[10px]">
                              {message.response.query_type}
                            </Badge>
                            <Badge variant="secondary" className="text-[10px]">
                              {message.response.retries_used} retries
                            </Badge>
                            <Badge
                              variant={message.response.grounded ? "secondary" : "destructive"}
                              className="text-[10px]"
                            >
                              {message.response.grounded ? "grounded" : "ungrounded"}
                            </Badge>
                          </div>
                        ) : null}

                        {message.trace ? (
                          <details className="group/trace mt-1">
                            <summary className="flex cursor-pointer list-none items-center gap-1.5 text-xs font-medium text-muted-foreground/70 transition-colors hover:text-muted-foreground">
                              <svg
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                strokeWidth="2"
                                className="size-3 transition-transform group-open/trace:rotate-90"
                              >
                                <path d="m9 18 6-6-6-6" strokeLinecap="round" strokeLinejoin="round" />
                              </svg>
                              View trace
                            </summary>
                            <div className="mt-3">
                              <TraceTimeline steps={message.trace.trace_steps} />
                            </div>
                          </details>
                        ) : null}

                        {message.response ? (
                          <FeedbackButtons traceId={message.response.trace_id} />
                        ) : null}
                      </div>
                    </div>
                  )}
                </motion.article>
              ))}
            </div>
          </div>
        </div>

        {/* ── Input bar — pinned at bottom of the flex column ───────── */}
        <div className="shrink-0 border-t
                        border-white/50 dark:border-white/[0.07]
                        bg-white/50 dark:bg-black/30
                        px-4 py-4 backdrop-blur-xl">
          <div className="mx-auto max-w-2xl">
            <ChatInput
              value={input}
              onChange={setInput}
              onSubmit={() => submit()}
              disabled={isLoading}
            />
          </div>
        </div>
      </div>

      <CitationDrawer
        citation={citation}
        open={Boolean(citation)}
        onOpenChange={(open) => !open && setCitation(null)}
      />
    </div>
  )
}
