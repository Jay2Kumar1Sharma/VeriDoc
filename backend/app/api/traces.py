import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_metadata_store
from app.schemas.api import TraceResponse, TracesResponse
from app.stores.metadata_store import MetadataStore, QueryTraceRecord

router = APIRouter(prefix="/traces", tags=["traces"])


@router.get("/{trace_id}", response_model=TraceResponse)
async def get_trace(
    trace_id: str,
    metadata_store: Annotated[MetadataStore, Depends(get_metadata_store)],
) -> TraceResponse:
    record = await metadata_store.get_query_trace(trace_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Trace not found.")
    return _trace_response(record)


@router.get("", response_model=TracesResponse)
async def list_traces(
    *,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    metadata_store: Annotated[MetadataStore, Depends(get_metadata_store)],
) -> TracesResponse:
    records = await metadata_store.list_query_traces(limit=limit, offset=offset)
    return TracesResponse(
        traces=[_trace_response(record) for record in records],
        limit=limit,
        offset=offset,
    )


def _trace_response(record: QueryTraceRecord) -> TraceResponse:
    payload = json.loads(record.payload_json)
    return TraceResponse(
        trace_id=record.trace_id,
        question=record.question,
        answer=record.answer,
        retries=record.retries,
        grounded=record.grounded,
        latency_ms=record.latency_ms,
        created_at=record.created_at,
        trace_steps=list(payload.get("trace", [])),
    )
