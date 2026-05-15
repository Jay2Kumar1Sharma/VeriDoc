"use client"

import { UploadCloud } from "lucide-react"
import { useState } from "react"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useDocuments, useIngestJob } from "@/hooks/useDocuments"

export function IngestDialog() {
  const [open, setOpen] = useState(false)
  const [urls, setUrls] = useState("")
  const [files, setFiles] = useState<File[]>([])
  const [jobId, setJobId] = useState<string | null>(null)
  const { ingestUrlMutation, uploadMutation } = useDocuments()
  const job = useIngestJob(jobId)

  const ingestUrls = async () => {
    const response = await ingestUrlMutation.mutateAsync(
      urls.split(/\n+/).map((url) => url.trim()).filter(Boolean),
    )
    setJobId(response.job_id ?? null)
  }

  const upload = async () => {
    const response = await uploadMutation.mutateAsync(files)
    setJobId(response.job_id ?? null)
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger render={<Button />}>
        <UploadCloud className="mr-2 size-4" />
        Ingest new
      </DialogTrigger>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Ingest documentation</DialogTitle>
        </DialogHeader>
        <Tabs defaultValue="urls">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="urls">From URLs</TabsTrigger>
            <TabsTrigger value="files">Upload files</TabsTrigger>
          </TabsList>
          <TabsContent value="urls" className="space-y-3">
            <textarea
              value={urls}
              onChange={(event) => setUrls(event.target.value)}
              className="h-36 w-full resize-none rounded-lg border bg-background p-3 text-sm outline-none focus:ring-2 focus:ring-ring"
              placeholder="https://fastapi.tiangolo.com/tutorial/"
            />
            <Button onClick={ingestUrls} disabled={!urls.trim() || ingestUrlMutation.isPending}>
              Start ingestion
            </Button>
          </TabsContent>
          <TabsContent value="files" className="space-y-3">
            <label className="flex h-36 cursor-pointer flex-col items-center justify-center rounded-lg border border-dashed text-sm text-muted-foreground hover:bg-muted/50">
              <UploadCloud className="mb-2 size-6" />
              Drop or choose Markdown files
              <input
                multiple
                type="file"
                accept=".md,.txt"
                className="sr-only"
                onChange={(event) => setFiles(Array.from(event.target.files ?? []))}
              />
            </label>
            <p className="text-xs text-muted-foreground">{files.length} selected</p>
            <Button onClick={upload} disabled={!files.length || uploadMutation.isPending}>
              Upload
            </Button>
          </TabsContent>
        </Tabs>
        {jobId ? (
          <div className="rounded-lg border bg-muted/40 p-3 text-sm">
            Job {jobId.slice(0, 8)}: {job.data?.status ?? "queued"}
          </div>
        ) : null}
      </DialogContent>
    </Dialog>
  )
}
