from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_metadata_store
from app.schemas.api import (
    SessionMessage,
    SessionMessagesResponse,
    SessionsResponse,
    SessionSummary,
)
from app.stores.metadata_store import MetadataStore

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("", response_model=SessionsResponse)
async def list_sessions(
    metadata_store: Annotated[MetadataStore, Depends(get_metadata_store)],
) -> SessionsResponse:
    records = await metadata_store.list_sessions()
    summaries: list[SessionSummary] = []
    for record in records:
        messages = await metadata_store.list_session_messages(record.session_id)
        preview = messages[0].content if messages else "New chat"
        summaries.append(
            SessionSummary(
                session_id=record.session_id,
                created_at=record.created_at,
                preview=preview[:120],
            )
        )
    return SessionsResponse(sessions=summaries)


@router.get("/{session_id}/messages", response_model=SessionMessagesResponse)
async def list_session_messages(
    session_id: str,
    metadata_store: Annotated[MetadataStore, Depends(get_metadata_store)],
) -> SessionMessagesResponse:
    messages = await metadata_store.list_session_messages(session_id)
    if not messages:
        session = await metadata_store.get_session(session_id)
        if session is None:
            raise HTTPException(status_code=404, detail="Session not found")
    return SessionMessagesResponse(
        messages=[
            SessionMessage(
                id=message.id,
                session_id=message.session_id,
                role=message.role,
                content=message.content,
                created_at=message.created_at,
            )
            for message in messages
        ]
    )
