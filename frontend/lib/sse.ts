import type { QueryResponse } from "@/lib/types"

export async function streamQuestion(
  question: string,
  onToken: (token: string) => void,
): Promise<QueryResponse | null> {
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000"}/query`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "text/event-stream",
      },
      body: JSON.stringify({ question }),
    },
  )

  if (!response.ok || !response.body) {
    throw new Error(await response.text())
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let finalResponse: QueryResponse | null = null
  let buffer = ""

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const events = buffer.split("\n\n")
    buffer = events.pop() ?? ""
    for (const event of events) handleEvent(event)
  }
  if (buffer) handleEvent(buffer)

  return finalResponse

  function handleEvent(event: string) {
    for (const line of event.split("\n")) {
      if (!line.startsWith("data: ")) continue
      const payload = JSON.parse(line.slice(6)) as {
        token?: string
        done?: boolean
        response?: QueryResponse
      }
      if (payload.token) onToken(payload.token)
      if (payload.done && payload.response) finalResponse = payload.response
    }
  }
}
