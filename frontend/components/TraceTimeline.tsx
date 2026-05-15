"use client"

import {
  AlertTriangle,
  Brain,
  CheckCircle2,
  FileQuestion,
  Globe2,
  PenLine,
  Search,
  ShieldCheck,
  Sparkles,
} from "lucide-react"

import { Badge } from "@/components/ui/badge"
import type { TraceStep } from "@/lib/types"

const icons = {
  query_analysis: Brain,
  retrieval: Search,
  grader: CheckCircle2,
  rewriter: PenLine,
  generator: Sparkles,
  hallucination_check: ShieldCheck,
  web_search: Globe2,
  fallback: FileQuestion,
}

export function TraceTimeline({ steps }: { steps: TraceStep[] }) {
  return (
    <div className="space-y-3" data-testid="trace-timeline">
      {steps.map((step, index) => {
        const Icon = icons[step.node as keyof typeof icons] ?? AlertTriangle
        return (
          <details key={`${step.node}-${index}`} className="group rounded-lg border bg-card p-3">
            <summary className="flex cursor-pointer list-none items-center justify-between gap-3">
              <span className="flex min-w-0 items-center gap-3">
                <span className="grid size-8 shrink-0 place-items-center rounded-md bg-primary/10 text-primary">
                  <Icon className="size-4" />
                </span>
                <span className="truncate text-sm font-medium">{label(step.node)}</span>
              </span>
              <Badge variant="secondary">{step.duration_ms ?? 0}ms</Badge>
            </summary>
            <pre className="mt-3 max-h-72 overflow-auto rounded-md bg-muted/50 p-3 text-xs leading-5">
              {JSON.stringify(step.output ?? {}, null, 2)}
            </pre>
          </details>
        )
      })}
    </div>
  )
}

function label(node: string) {
  return node.replaceAll("_", " ")
}
