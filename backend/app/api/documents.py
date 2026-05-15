from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.api.deps import get_metadata_store, get_vector_store
from app.schemas.api import DocumentsResponse, DocumentSummary
from app.stores.metadata_store import DocumentRecord, MetadataStore
from app.stores.vector_store import VectorStore

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=DocumentsResponse)
async def list_documents(
    *,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    source: str | None = None,
    metadata_store: Annotated[MetadataStore, Depends(get_metadata_store)],
) -> DocumentsResponse:
    records = await metadata_store.list_documents(limit=limit, offset=offset, source=source)
    return DocumentsResponse(
        documents=[_summary(record) for record in records],
        limit=limit,
        offset=offset,
    )


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    doc_id: str,
    metadata_store: Annotated[MetadataStore, Depends(get_metadata_store)],
    vector_store: Annotated[VectorStore, Depends(get_vector_store)],
) -> Response:
    record = await metadata_store.get_document(doc_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    vector_store.delete_by_source(record.source)
    await metadata_store.delete_document(doc_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _summary(record: DocumentRecord) -> DocumentSummary:
    return DocumentSummary(
        doc_id=record.doc_id,
        source=record.source,
        title=record.title,
        ingested_at=record.ingested_at,
        chunk_count=record.chunk_count,
        status=record.status,
    )
