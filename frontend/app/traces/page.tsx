"use client"

import { Activity } from "lucide-react"
import { useState } from "react"

import { TraceTimeline } from "@/components/TraceTimeline"
import { Badge } from "@/components/ui/badge"
import { useTrace, useTraces } from "@/hooks/useTraces"

function latencyColor(ms: number) {
  if (ms < 1500) return "text-emerald-600 dark:text-emerald-400"
  if (ms < 4000) return "text-amber-600 dark:text-amber-400"
  return "text-red-600 dark:text-red-400"
}

export default function TracesPage() {
  const traces = useTraces()
  const [selected, setSelected] = useState<string | null>(null)
  const detail = useTrace(selected)

  const traceList = traces.data?.traces ?? []

  return (
    <div className="mx-auto grid max-w-7xl gap-6 px-4 py-8 md:px-8 lg:grid-cols-[1fr_400px]">
      {/* Table section */}
      <section>
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold">Traces</h1>
            <p className="mt-1 text-sm text-muted-foreground">
              Execution history of RAG pipeline runs
            </p>
          </div>
          {traceList.length > 0 && (
            <Badge variant="secondary" className="text-xs">
              {traceList.length} runs
            </Badge>
          )}
        </div>

        {traceList.length === 0 ? (
          <div className="flex flex-col items-center justify-center rounded-2xl py-16 text-center
                          border border-dashed border-white/50 dark:border-white/[0.08]
                          bg-white/30 dark:bg-white/[0.02]
                          backdrop-blur-lg">
            <div className="mb-3 grid size-12 place-items-center rounded-xl bg-muted/60">
              <Activity className="size-6 text-muted-foreground" />
            </div>
            <p className="text-sm font-medium">No traces recorded yet</p>
            <p className="mt-1 text-xs text-muted-foreground">
              Ask a question to generate your first trace
            </p>
          </div>
        ) : (
          <div className="overflow-hidden rounded-2xl
                          border border-white/55 dark:border-white/[0.08]
                          bg-white/50 dark:bg-white/[0.04]
                          backdrop-blur-xl shadow-sm shadow-black/5">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/50 dark:border-white/[0.07]
                               bg-white/30 dark:bg-white/[0.04]">
                  {["Question", "Retries", "Grounded", "Latency"].map((h) => (
                    <th key={h} className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-white/30 dark:divide-white/[0.05]">
                {traceList.map((trace) => {
                  const isSelected = trace.trace_id === selected
                  return (
                    <tr
                      key={trace.trace_id}
                      className={`cursor-pointer transition-colors ${
                        isSelected
                          ? "bg-primary/8 dark:bg-primary/[0.12]"
                          : "hover:bg-white/40 dark:hover:bg-white/[0.04]"
                      }`}
                      onClick={() => setSelected(isSelected ? null : trace.trace_id)}
                    >
                      <td className="max-w-xs truncate px-4 py-3 font-medium">{trace.question}</td>
                      <td className="px-4 py-3">
                        <Badge variant="secondary" className="text-[10px]">{trace.retries}</Badge>
                      </td>
                      <td className="px-4 py-3">
                        <Badge
                          variant={trace.grounded ? "secondary" : "destructive"}
                          className="text-[10px]"
                        >
                          {trace.grounded ? "yes" : "no"}
                        </Badge>
                      </td>
                      <td className={`px-4 py-3 font-mono text-xs font-medium ${latencyColor(trace.latency_ms)}`}>
                        {trace.latency_ms < 1000
                          ? `${trace.latency_ms}ms`
                          : `${(trace.latency_ms / 1000).toFixed(1)}s`}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* Detail panel — glass */}
      <aside className="rounded-2xl p-5
                        border border-white/55 dark:border-white/[0.08]
                        bg-white/50 dark:bg-white/[0.04]
                        backdrop-blur-xl shadow-sm shadow-black/5">
        <h2 className="font-semibold">Trace detail</h2>
        {detail.data ? (
          <div className="mt-4 space-y-4">
            <p className="text-sm leading-relaxed text-muted-foreground">{detail.data.answer}</p>
            <TraceTimeline steps={detail.data.trace_steps} />
          </div>
        ) : (
          <div className="mt-8 flex flex-col items-center text-center">
            <Activity className="mb-2 size-8 text-muted-foreground/30" />
            <p className="text-sm text-muted-foreground">Select a row to inspect node execution.</p>
          </div>
        )}
      </aside>
    </div>
  )
}
