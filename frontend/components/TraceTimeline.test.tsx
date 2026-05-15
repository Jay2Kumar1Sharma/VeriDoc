import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"

import { TraceTimeline } from "@/components/TraceTimeline"

describe("TraceTimeline", () => {
  it("renders all expected node types", () => {
    render(
      <TraceTimeline
        steps={[
          { node: "query_analysis", duration_ms: 1, output: {} },
          { node: "retrieval", duration_ms: 2, output: {} },
          { node: "grader", duration_ms: 3, output: {} },
          { node: "rewriter", duration_ms: 4, output: {} },
          { node: "generator", duration_ms: 5, output: {} },
          { node: "hallucination_check", duration_ms: 6, output: {} },
        ]}
      />,
    )

    expect(screen.getByText("query analysis")).toBeInTheDocument()
    expect(screen.getByText("retrieval")).toBeInTheDocument()
    expect(screen.getByText("grader")).toBeInTheDocument()
    expect(screen.getByText("rewriter")).toBeInTheDocument()
    expect(screen.getByText("generator")).toBeInTheDocument()
    expect(screen.getByText("hallucination check")).toBeInTheDocument()
  })
})

