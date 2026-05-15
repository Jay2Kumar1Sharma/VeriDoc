"use client"

import { useQuery } from "@tanstack/react-query"

import { getTrace, listTraces } from "@/lib/api"

export function useTraces() {
  return useQuery({
    queryKey: ["traces"],
    queryFn: listTraces,
  })
}

export function useTrace(traceId: string | null) {
  return useQuery({
    queryKey: ["trace", traceId],
    queryFn: () => getTrace(traceId ?? ""),
    enabled: Boolean(traceId),
  })
}

