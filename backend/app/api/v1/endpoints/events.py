"""Events API endpoints."""

from datetime import datetime
from math import ceil
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.errors import ValidationError
from app.core.database import get_session
from app.models.event import (
    EventCreate,
    EventDraft,
    EventListResponse,
    EventResponse,
    EventUpdate,
)
from app.services.ai_service import AIService
from app.services.event_service import EventService

router = APIRouter()


@router.get("/", response_model=EventListResponse)
async def list_events(
    session: Annotated[AsyncSession, Depends(get_session)],
    from_date: datetime | None = Query(None, alias="from"),
    to_date: datetime | None = Query(None, alias="to"),
    query: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
) -> EventListResponse:
    """List events with optional filtering and pagination."""
    events, total = await EventService.list_events(
        session=session,
        from_date=from_date,
        to_date=to_date,
        query=query,
        page=page,
        size=size,
    )

    pages = ceil(total / size) if total > 0 else 1

    return EventListResponse(
        events=[EventResponse.model_validate(event) for event in events],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> EventResponse:
    """Get a specific event by ID."""
    event = await EventService.get_event(session, event_id)
    return EventResponse.model_validate(event)


@router.post("/", response_model=EventResponse, status_code=201)
async def create_event(
    event_data: EventCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> EventResponse:
    """Create a new event."""
    event = await EventService.create_event(session, event_data)
    return EventResponse.model_validate(event)


@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: int,
    event_data: EventUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> EventResponse:
    """Update an existing event."""
    event = await EventService.update_event(session, event_id, event_data)
    return EventResponse.model_validate(event)


@router.delete("/{event_id}", status_code=204)
async def delete_event(
    event_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    """Delete an event."""
    await EventService.delete_event(session, event_id)


@router.post("/draft", response_model=EventDraft)
async def create_event_draft(
    draft_request: dict[str, str],
) -> EventDraft:
    """Generate an event draft from natural language prompt."""
    prompt = draft_request.get("prompt", "")
    if not prompt:
        raise ValidationError("Prompt is required")

    draft = await AIService.generate_event_draft(prompt)
    return draft
