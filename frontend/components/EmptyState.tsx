"use client"

import { BookOpen, Code2, SearchCheck, ShieldCheck } from "lucide-react"

const examples = [
  "How do I declare path parameters in FastAPI?",
  "How does FastAPI parse request bodies?",
  "When should dependencies be used?",
  "How should retryable errors be handled?",
]

export function EmptyState({ onExample }: { onExample: (query: string) => void }) {
  return (
    <section className="mx-auto flex min-h-[60vh] max-w-3xl flex-col items-center justify-center px-4 text-center">
      <div className="mb-6 grid grid-cols-4 gap-3 text-primary">
        <BookOpen className="size-6" />
        <SearchCheck className="size-6" />
        <ShieldCheck className="size-6" />
        <Code2 className="size-6" />
      </div>
      <h1 className="text-4xl font-semibold tracking-normal md:text-5xl">
        Ask anything about the docs
      </h1>
      <p className="mt-4 max-w-xl text-sm leading-6 text-muted-foreground">
        VeriDoc retrieves, grades, rewrites, and checks grounding before it answers.
      </p>
      <div className="mt-8 flex flex-wrap justify-center gap-2">
        {examples.map((example) => (
          <button
            key={example}
            type="button"
            onClick={() => onExample(example)}
            className="rounded-full border px-3 py-1.5 text-xs text-muted-foreground hover:bg-muted hover:text-foreground"
          >
            {example}
          </button>
        ))}
      </div>
    </section>
  )
}

