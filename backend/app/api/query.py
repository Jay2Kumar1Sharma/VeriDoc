import json
from time import perf_counter
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from app.api.deps import GraphRunner, get_graph, get_metadata_store
from app.core.logging import trace_id_var
from app.graph.state import initial_state
from app.schemas.api import QueryRequest, QueryResponse
from app.schemas.types import Citation
from app.stores.metadata_store import MetadataStore

router = APIRouter(prefix="/query", tags=["query"])


@router.post("", response_model=QueryResponse)
async def query(
    payload: QueryRequest,
    request: Request,
    graph: Annotated[GraphRunner, Depends(get_graph)],
    metadata_store: Annotated[MetadataStore, Depends(get_metadata_store)],
) -> QueryResponse | StreamingResponse:
    if "text/event-stream" in request.headers.get("accept", ""):
        return StreamingResponse(
            _query_sse(payload, graph, metadata_store),
            media_type="text/event-stream",
        )
    return await _run_query(payload, graph, metadata_store)


async def _query_sse(
    payload: QueryRequest,
    graph: GraphRunner,
    metadata_store: MetadataStore,
):
    response = await _run_query(payload, graph, metadata_store)
    trace = await metadata_store.get_query_trace(response.trace_id)
    trace_steps: list[dict[str, object]] = []
    if trace is not None:
        stored_payload = json.loads(trace.payload_json)
        trace_steps = list(stored_payload.get("trace", []))
    for step in trace_steps:
        yield f": node {step.get('node')} {step.get('duration_ms')}ms\n\n"
    for token in response.answer.split(" "):
        yield f"data: {json.dumps({'token': token + ' '})}\n\n"
    yield f"data: {json.dumps({'done': True, 'trace_id': response.trace_id})}\n\n"


async def _run_query(
    payload: QueryRequest,
    graph: GraphRunner,
    metadata_store: MetadataStore,
) -> QueryResponse:
    trace_id = trace_id_var.get() or str(uuid4())
    start = perf_counter()
    result = await graph.ainvoke(
        initial_state(
            question=payload.question,
            session_id=payload.session_id,
            max_retries=payload.max_retries,
        ),
        config={"configurable": {"thread_id": payload.session_id or trace_id}},
    )
    latency_ms = int((perf_counter() - start) * 1000)
    hallucination_check = result.get("hallucination_check") or {}
    grounded = bool(hallucination_check.get("grounded", False))
    citations = [_citation_from_any(item) for item in result.get("citations", [])]
    response = QueryResponse(
        trace_id=trace_id,
        answer=str(result.get("answer", "")),
        citations=citations,
        query_type=result.get("query_type", "conceptual"),
        retries_used=int(result.get("retry_count", 0)),
        grounded=grounded,
        latency_ms=latency_ms,
    )
    await metadata_store.upsert_query_trace(
        trace_id=trace_id,
        question=payload.question,
        answer=response.answer,
        retries=response.retries_used,
        grounded=response.grounded,
        latency_ms=latency_ms,
        payload_json=json.dumps(_jsonable_result(result)),
    )
    return response


def _citation_from_any(value: object) -> Citation:
    if isinstance(value, Citation):
        return value
    if isinstance(value, dict):
        return Citation.model_validate(value)
    msg = f"Unsupported citation value: {type(value)!r}"
    raise TypeError(msg)


def _jsonable_result(result: dict[str, object]) -> dict[str, object]:
    encoded = json.loads(
        json.dumps(
            result,
            default=lambda value: (
                value.model_dump() if hasattr(value, "model_dump") else str(value)
            ),
        )
    )
    return dict(encoded)
