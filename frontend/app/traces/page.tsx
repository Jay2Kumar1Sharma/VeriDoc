"use client"

import { useState } from "react"

import { TraceTimeline } from "@/components/TraceTimeline"
import { Badge } from "@/components/ui/badge"
import { useTrace, useTraces } from "@/hooks/useTraces"

export default function TracesPage() {
  const traces = useTraces()
  const [selected, setSelected] = useState<string | null>(null)
  const detail = useTrace(selected)

  return (
    <div className="mx-auto grid max-w-7xl gap-6 px-4 py-8 lg:grid-cols-[1fr_420px]">
      <section>
        <h1 className="text-2xl font-semibold">Traces</h1>
        <div className="mt-6 overflow-hidden rounded-lg border">
          <table className="w-full text-sm">
            <thead className="bg-muted/60 text-left text-xs uppercase text-muted-foreground">
              <tr>
                <th className="px-4 py-3">Question</th>
                <th className="px-4 py-3">Retries</th>
                <th className="px-4 py-3">Grounded</th>
                <th className="px-4 py-3">Latency</th>
              </tr>
            </thead>
            <tbody>
              {traces.data?.traces.map((trace) => (
                <tr
                  key={trace.trace_id}
                  className="cursor-pointer border-t hover:bg-muted/50"
                  onClick={() => setSelected(trace.trace_id)}
                >
                  <td className="max-w-md truncate px-4 py-3">{trace.question}</td>
                  <td className="px-4 py-3"><Badge variant="secondary">{trace.retries}</Badge></td>
                  <td className="px-4 py-3">
                    <Badge variant={trace.grounded ? "secondary" : "destructive"}>
                      {trace.grounded ? "yes" : "no"}
                    </Badge>
                  </td>
                  <td className="px-4 py-3 text-muted-foreground">{trace.latency_ms}ms</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
      <aside className="rounded-lg border bg-card p-4">
        <h2 className="font-medium">Trace detail</h2>
        {detail.data ? (
          <div className="mt-4 space-y-4">
            <p className="text-sm text-muted-foreground">{detail.data.answer}</p>
            <TraceTimeline steps={detail.data.trace_steps} />
          </div>
        ) : (
          <p className="mt-4 text-sm text-muted-foreground">Select a trace to inspect node execution.</p>
        )}
      </aside>
    </div>
  )
}

