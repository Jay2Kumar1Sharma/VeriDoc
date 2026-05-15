import { fireEvent, render, screen } from "@testing-library/react"
import { describe, expect, it, vi } from "vitest"

import { AnswerRenderer } from "@/components/AnswerRenderer"
import type { Citation } from "@/lib/types"

const citation: Citation = {
  chunk_id: "chunk_1",
  source: "docs.md",
  title: "Docs",
  snippet: "FastAPI uses path parameters.",
  header_path: ["Tutorial"],
}

describe("AnswerRenderer", () => {
  it("renders citations as clickable pills", () => {
    const onCitationClick = vi.fn()

    render(
      <AnswerRenderer
        content="Use braces for path parameters. [#chunk_1]"
        citations={[citation]}
        onCitationClick={onCitationClick}
      />,
    )

    fireEvent.click(screen.getByRole("button", { name: /open citation chunk_1/i }))

    expect(screen.getByText("chunk_1")).toBeInTheDocument()
    expect(onCitationClick).toHaveBeenCalledWith(citation)
  })
})

