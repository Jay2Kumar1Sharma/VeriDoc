"use client"

import { useQuery } from "@tanstack/react-query"

import { listSessionMessages, listSessions } from "@/lib/api"

export function useSessions() {
  return useQuery({
    queryKey: ["sessions"],
    queryFn: listSessions,
    refetchInterval: 30000,
  })
}

export function useSessionMessages(sessionId: string | null, enabled = Boolean(sessionId)) {
  return useQuery({
    queryKey: ["sessions", sessionId, "messages"],
    queryFn: () => listSessionMessages(sessionId ?? ""),
    enabled,
  })
}
