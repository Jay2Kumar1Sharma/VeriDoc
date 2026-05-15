"use client"

import { useState } from "react"
import { toast } from "sonner"

import { getTrace } from "@/lib/api"
import { streamQuestion } from "@/lib/sse"
import type { ChatMessage } from "@/lib/types"

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const send = async (question: string) => {
    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: question,
    }
    const assistantId = crypto.randomUUID()
    setMessages((current) => [
      ...current,
      userMessage,
      { id: assistantId, role: "assistant", content: "" },
    ])
    setIsLoading(true)

    try {
      const response = await streamQuestion(question, (token) => {
        setMessages((current) =>
          current.map((message) =>
            message.id === assistantId
              ? { ...message, content: `${message.content}${token}` }
              : message,
          ),
        )
      })
      if (!response) throw new Error("Streaming response did not include a final payload")
      const trace = await getTrace(response.trace_id)
      setMessages((current) =>
        current.map((message) =>
          message.id === assistantId
            ? { ...message, content: response.answer, response, trace }
            : message,
        ),
      )
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Query failed")
      setMessages((current) => current.filter((message) => message.id !== assistantId))
    } finally {
      setIsLoading(false)
    }
  }

  return { messages, send, isLoading }
}
