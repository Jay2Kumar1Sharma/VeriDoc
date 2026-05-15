"use client"

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"

import { deleteDocument, getIngestJob, ingestUrls, listDocuments, uploadFiles } from "@/lib/api"

export function useDocuments() {
  const queryClient = useQueryClient()
  const documents = useQuery({
    queryKey: ["documents"],
    queryFn: listDocuments,
  })

  const remove = useMutation({
    mutationFn: deleteDocument,
    onSuccess: async () => {
      toast.success("Document deleted")
      await queryClient.invalidateQueries({ queryKey: ["documents"] })
    },
  })

  const ingestUrlMutation = useMutation({
    mutationFn: ingestUrls,
    onSuccess: async () => {
      toast.success("Ingestion started")
      await queryClient.invalidateQueries({ queryKey: ["documents"] })
    },
  })

  const uploadMutation = useMutation({
    mutationFn: uploadFiles,
    onSuccess: async () => {
      toast.success("Upload ingested")
      await queryClient.invalidateQueries({ queryKey: ["documents"] })
    },
  })

  return { documents, remove, ingestUrlMutation, uploadMutation }
}

export function useIngestJob(jobId: string | null) {
  return useQuery({
    queryKey: ["ingest-job", jobId],
    queryFn: () => getIngestJob(jobId ?? ""),
    enabled: Boolean(jobId),
    refetchInterval: (query) => {
      const status = query.state.data?.status
      return status === "queued" || status === "running" ? 1000 : false
    },
  })
}

