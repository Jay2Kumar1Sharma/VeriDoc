"use client"

import { ArrowRight, CheckCircle2, Globe2, PenLine, Search } from "lucide-react"

const features = [
  { icon: Search, label: "Retrieves relevant chunks" },
  { icon: CheckCircle2, label: "Grades document relevance" },
  { icon: PenLine, label: "Rewrites poor queries" },
  { icon: Globe2, label: "Falls back to web search" },
]

const examples = [
  "How do I declare path parameters in FastAPI?",
  "How does FastAPI parse request bodies?",
  "When should dependencies be used?",
  "How should retryable errors be handled?",
]

export function EmptyState({ onExample }: { onExample: (query: string) => void }) {
  return (
    <section className="mx-auto flex max-w-xl flex-col items-center py-16 text-center">
      {/* Logo mark */}
      <div className="mb-7 flex size-[4.5rem] items-center justify-center rounded-[1.4rem]
                      border border-white/60 dark:border-white/[0.12]
                      bg-white/50 dark:bg-white/[0.07]
                      backdrop-blur-xl shadow-xl shadow-primary/15 dark:shadow-primary/25
                      ring-4 ring-primary/10 dark:ring-primary/15">
        <svg
          viewBox="0 0 24 24"
          fill="none"
          className="size-8 text-primary"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
          <path d="m9 12 2 2 4-4" />
        </svg>
      </div>

      <h1 className="text-3xl font-semibold tracking-tight text-balance md:text-[2.5rem] md:leading-tight">
        Ask anything about your docs
      </h1>
      <p className="mt-3 max-w-sm text-[0.9rem] leading-relaxed text-muted-foreground">
        VeriDoc retrieves, grades, rewrites, and checks grounding — every answer is backed by real sources.
      </p>

      {/* Feature grid — glass cards */}
      <div className="mt-9 grid w-full max-w-sm grid-cols-2 gap-2">
        {features.map(({ icon: Icon, label }) => (
          <div
            key={label}
            className="flex items-center gap-2 rounded-xl px-3 py-2.5 text-xs text-muted-foreground
                       border border-white/50 dark:border-white/[0.08]
                       bg-white/45 dark:bg-white/[0.04]
                       backdrop-blur-lg"
          >
            <Icon className="size-3.5 shrink-0 text-primary/80" />
            {label}
          </div>
        ))}
      </div>

      {/* Example prompts — glass buttons */}
      <div className="mt-5 flex w-full max-w-sm flex-col gap-1.5">
        <p className="mb-1.5 text-left text-[10px] font-semibold uppercase tracking-wider text-muted-foreground/50">
          Try asking
        </p>
        {examples.map((example) => (
          <button
            key={example}
            type="button"
            onClick={() => onExample(example)}
            className="group flex items-center gap-3 rounded-xl px-4 py-2.5 text-left text-sm text-muted-foreground
                       border border-white/50 dark:border-white/[0.07]
                       bg-white/40 dark:bg-white/[0.03]
                       backdrop-blur-lg
                       transition-all duration-150
                       hover:border-primary/30 dark:hover:border-primary/20
                       hover:bg-white/65 dark:hover:bg-white/[0.07]
                       hover:text-foreground"
          >
            <ArrowRight className="size-3 shrink-0 text-primary/40 transition-transform group-hover:translate-x-0.5 group-hover:text-primary/70" />
            {example}
          </button>
        ))}
      </div>
    </section>
  )
}
