import { fireEvent, render, screen } from "@testing-library/react"
import { describe, expect, it, vi } from "vitest"

import { CitationPill } from "@/components/CitationPill"
import type { Citation } from "@/lib/types"

describe("CitationPill", () => {
  it("calls onClick with the citation", () => {
    const citation: Citation = {
      chunk_id: "abc",
      source: "source.md",
      title: "Source",
      snippet: "Snippet",
      header_path: [],
    }
    const onClick = vi.fn()

    render(<CitationPill citation={citation} onClick={onClick} />)
    fireEvent.click(screen.getByRole("button", { name: /open citation abc/i }))

    expect(onClick).toHaveBeenCalledWith(citation)
  })
})

