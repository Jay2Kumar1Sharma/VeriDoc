"use client"

import { useQuery } from "@tanstack/react-query"

import { getHealth } from "@/lib/api"

export function StatusPill() {
  const { data, isError } = useQuery({
    queryKey: ["health"],
    queryFn: getHealth,
    refetchInterval: 30000,
    retry: false,
  })

  const ok = Boolean(data) && !isError

  return (
    <div className="flex items-center gap-2 rounded-full border px-3 py-1 text-xs text-muted-foreground">
      <span className={`size-2 rounded-full ${ok ? "bg-emerald-500" : "bg-red-500"}`} />
      {ok ? `${data?.llm_provider} online` : "offline"}
    </div>
  )
}

