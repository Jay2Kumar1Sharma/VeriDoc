from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.api.deps import get_metadata_store
from app.schemas.api import FeedbackRequest
from app.stores.metadata_store import MetadataStore

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", status_code=status.HTTP_204_NO_CONTENT)
async def feedback(
    payload: FeedbackRequest,
    metadata_store: Annotated[MetadataStore, Depends(get_metadata_store)],
) -> Response:
    trace = await metadata_store.get_query_trace(payload.trace_id)
    if trace is None:
        raise HTTPException(status_code=404, detail="Trace not found.")
    await metadata_store.add_feedback(
        trace_id=payload.trace_id,
        rating=payload.rating,
        comment=payload.comment,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
