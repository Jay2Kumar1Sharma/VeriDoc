"use client"

import "highlight.js/styles/github-dark.css"

import { Check, Copy } from "lucide-react"
import { useMemo, useState } from "react"
import ReactMarkdown from "react-markdown"
import rehypeHighlight from "rehype-highlight"
import remarkGfm from "remark-gfm"

import { CitationPill } from "@/components/CitationPill"
import { Button } from "@/components/ui/button"
import type { Citation } from "@/lib/types"

const citationPattern = /\[#([A-Za-z0-9_.:-]+)\]/g

export function AnswerRenderer({
  content,
  citations,
  onCitationClick,
}: {
  content: string
  citations: Citation[]
  onCitationClick: (citation: Citation) => void
}) {
  const citationMap = useMemo(
    () => new Map(citations.map((citation) => [citation.chunk_id, citation])),
    [citations],
  )

  return (
    <div className="prose prose-sm max-w-none dark:prose-invert prose-pre:p-0">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeHighlight]}
        components={{
          p({ children }) {
            return <p className="leading-7">{renderCitations(children, citationMap, onCitationClick)}</p>
          },
          code({ className, children }) {
            const language = className?.replace("language-", "")
            return (
              <CodeBlock language={language}>
                {String(children).replace(/\n$/, "")}
              </CodeBlock>
            )
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}

function renderCitations(
  children: React.ReactNode,
  citationMap: Map<string, Citation>,
  onCitationClick: (citation: Citation) => void,
): React.ReactNode {
  if (typeof children === "string") {
    return renderText(children, citationMap, onCitationClick)
  }
  if (Array.isArray(children)) {
    return children.map((child, index) =>
        typeof child === "string" ? (
          <span key={index}>{renderText(child, citationMap, onCitationClick)}</span>
        ) : (
          child
        ),
      )
  }
  return children
}

function renderText(
  text: string,
  citationMap: Map<string, Citation>,
  onCitationClick: (citation: Citation) => void,
) {
  const parts: React.ReactNode[] = []
  let lastIndex = 0
  for (const match of Array.from(text.matchAll(citationPattern))) {
    const chunkId = match[1]
    const citation = citationMap.get(chunkId)
    parts.push(text.slice(lastIndex, match.index))
    if (citation) {
      parts.push(
        <CitationPill key={`${chunkId}-${match.index}`} citation={citation} onClick={onCitationClick} />,
      )
    } else {
      parts.push(match[0])
    }
    lastIndex = (match.index ?? 0) + match[0].length
  }
  parts.push(text.slice(lastIndex))
  return parts
}

function CodeBlock({ language, children }: { language?: string; children: string }) {
  const [copied, setCopied] = useState(false)

  return (
    <div className="group relative overflow-hidden rounded-lg border bg-[#0d1117]">
      <div className="flex items-center justify-between border-b border-white/10 px-3 py-2">
        <span className="text-xs uppercase text-slate-400">{language ?? "text"}</span>
        <Button
          aria-label="Copy code"
          size="icon-sm"
          variant="ghost"
          onClick={async () => {
            await navigator.clipboard.writeText(children)
            setCopied(true)
            window.setTimeout(() => setCopied(false), 1200)
          }}
        >
          {copied ? <Check className="size-3.5" /> : <Copy className="size-3.5" />}
        </Button>
      </div>
      <pre className="overflow-x-auto p-4 text-sm">
        <code className={language ? `language-${language}` : undefined}>{children}</code>
      </pre>
    </div>
  )
}
