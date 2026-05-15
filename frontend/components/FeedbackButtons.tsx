"use client"

import { ThumbsDown, ThumbsUp } from "lucide-react"
import { useState } from "react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { sendFeedback } from "@/lib/api"

export function FeedbackButtons({ traceId }: { traceId: string }) {
  const [comment, setComment] = useState("")
  const [showComment, setShowComment] = useState(false)

  const submit = async (rating: 1 | -1) => {
    await sendFeedback(traceId, rating, rating === -1 ? comment : undefined)
    toast.success("Feedback saved")
    setShowComment(false)
    setComment("")
  }

  return (
    <div className="mt-3 space-y-2">
      <div className="flex items-center gap-2">
        <Button size="icon-sm" variant="ghost" aria-label="Helpful" onClick={() => submit(1)}>
          <ThumbsUp className="size-4" />
        </Button>
        <Button size="icon-sm" variant="ghost" aria-label="Not helpful" onClick={() => setShowComment(true)}>
          <ThumbsDown className="size-4" />
        </Button>
      </div>
      {showComment ? (
        <div className="flex gap-2">
          <input
            value={comment}
            onChange={(event) => setComment(event.target.value)}
            className="h-8 flex-1 rounded-md border bg-background px-3 text-sm"
            placeholder="What was missing?"
          />
          <Button size="sm" onClick={() => submit(-1)}>
            Send
          </Button>
        </div>
      ) : null}
    </div>
  )
}

