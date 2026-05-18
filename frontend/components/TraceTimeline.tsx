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
    <div className="relative ml-0.5 pl-3" data-testid="trace-timeline">
      {/* Vertical connecting line */}
      {steps.length > 1 && (
        <div className="absolute left-3.5 top-3.5 bottom-3.5 w-px bg-border" />
      )}

      <div className="space-y-2">
        {steps.map((step, index) => {
          const Icon = icons[step.node as keyof typeof icons] ?? AlertTriangle
          return (
            <div key={`${step.node}-${index}`} className="relative flex gap-3">
              {/* Circular node icon */}
              <div className="relative z-10 mt-2.5 flex size-7 shrink-0 items-center justify-center rounded-full border bg-card shadow-sm">
                <Icon className="size-3.5 text-primary" />
              </div>

              {/* Step content */}
              <details className="flex-1 overflow-hidden rounded-lg border bg-card/60 pb-0 text-xs backdrop-blur-sm">
                <summary className="flex cursor-pointer list-none items-center justify-between gap-2 px-3 py-2.5 hover:bg-muted/40 transition-colors">
                  <span className="font-medium text-foreground/80">{label(step.node)}</span>
                  <Badge variant="secondary" className="shrink-0 text-[10px]">
                    {step.duration_ms ?? 0}ms
                  </Badge>
                </summary>
                <div className="border-t">
                  <pre className="max-h-52 overflow-auto bg-muted/30 p-3 text-[11px] leading-5">
                    {JSON.stringify(step.output ?? {}, null, 2)}
                  </pre>
                </div>
              </details>
            </div>
          )
        })}
      </div>
    </div>
  )
}

function label(node: string) {
  return node.replaceAll("_", " ")
}
