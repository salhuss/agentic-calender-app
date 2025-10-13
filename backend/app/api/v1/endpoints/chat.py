"""Chat endpoints."""
import json
from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.models.chat import (
    ChatMessage,
    ChatMessageCreate,
    ChatMessageResponse,
    ChatResponse,
)
from app.models.event import Event
from app.services.llm import get_llm_provider

router = APIRouter()


@router.post("/message", response_model=ChatResponse)
async def send_message(
    message_data: ChatMessageCreate,
    session: AsyncSession = Depends(get_session),
) -> ChatResponse:
    """
    Send a message to the AI assistant.

    This endpoint:
    1. Saves the user message
    2. Gathers calendar context (recent and upcoming events)
    3. Sends to LLM with context
    4. Saves and returns the assistant's response
    """
    # Save user message
    user_message = ChatMessage(
        role="user",
        content=message_data.message,
        created_at=datetime.utcnow(),
    )
    session.add(user_message)
    await session.commit()
    await session.refresh(user_message)

    try:
        # Get calendar context
        context = await _get_calendar_context(session)

        # Get recent conversation history
        history = await _get_conversation_history(session, limit=10)

        # Prepare messages for LLM
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in history
            if msg.id != user_message.id  # Exclude the just-added message
        ]
        messages.append({"role": "user", "content": message_data.message})

        # Generate response using LLM
        llm = get_llm_provider()
        response_content = await llm.generate(messages=messages, context=context)

        # Save assistant response
        assistant_message = ChatMessage(
            role="assistant",
            content=response_content,
            context=json.dumps(context) if context else None,
            created_at=datetime.utcnow(),
        )
        session.add(assistant_message)
        await session.commit()
        await session.refresh(assistant_message)

        return ChatResponse(
            response=response_content,
            message_id=assistant_message.id,
        )

    except Exception as e:
        # If LLM fails, still save an error message
        error_response = f"I'm having trouble processing your request right now. Error: {str(e)}"
        assistant_message = ChatMessage(
            role="assistant",
            content=error_response,
            created_at=datetime.utcnow(),
        )
        session.add(assistant_message)
        await session.commit()
        await session.refresh(assistant_message)

        raise HTTPException(status_code=500, detail=error_response)


@router.get("/history", response_model=List[ChatMessageResponse])
async def get_chat_history(
    limit: int = 50,
    session: AsyncSession = Depends(get_session),
) -> List[ChatMessageResponse]:
    """Get chat history."""
    messages = await _get_conversation_history(session, limit=limit)
    return [
        ChatMessageResponse(
            id=msg.id,
            role=msg.role,
            content=msg.content,
            created_at=msg.created_at,
        )
        for msg in messages
    ]


@router.delete("/history")
async def clear_chat_history(
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Clear all chat history."""
    statement = select(ChatMessage)
    result = await session.execute(statement)
    messages = result.scalars().all()
    for message in messages:
        await session.delete(message)
    await session.commit()
    return {"message": "Chat history cleared", "deleted_count": len(messages)}


@router.get("/health")
async def chat_health_check() -> dict:
    """Check if chat service and LLM are available."""
    llm = get_llm_provider()
    is_healthy = await llm.health_check()

    if not is_healthy:
        raise HTTPException(
            status_code=503,
            detail="LLM service is not available. Make sure Ollama is running.",
        )

    return {
        "status": "healthy",
        "llm_provider": type(llm).__name__,
    }


async def _get_calendar_context(session: AsyncSession) -> dict:
    """
    Get calendar context for the LLM.

    Returns upcoming events and identifies free time slots.
    """
    now = datetime.utcnow()
    two_weeks_later = now + timedelta(days=14)

    # Get upcoming events
    statement = (
        select(Event)
        .where(Event.start_datetime >= now.isoformat())
        .where(Event.start_datetime <= two_weeks_later.isoformat())
        .order_by(Event.start_datetime)
    )
    result = await session.execute(statement)
    events = result.scalars().all()

    # Convert events to simple dict format for context
    events_data = [
        {
            "title": event.title,
            "start_datetime": event.start_datetime if isinstance(event.start_datetime, str) else event.start_datetime.isoformat() if event.start_datetime else None,
            "end_datetime": event.end_datetime if isinstance(event.end_datetime, str) else event.end_datetime.isoformat() if event.end_datetime else None,
            "all_day": event.all_day,
            "location": event.location,
        }
        for event in events
    ]

    # TODO: Calculate free time slots based on events
    free_times = _calculate_free_times(events_data)

    return {
        "events": events_data,
        "free_times": free_times,
        "current_time": now.isoformat(),
    }


async def _get_conversation_history(session: AsyncSession, limit: int = 10) -> List[ChatMessage]:
    """Get recent conversation history."""
    statement = (
        select(ChatMessage).order_by(ChatMessage.created_at.desc()).limit(limit)
    )
    result = await session.execute(statement)
    messages = result.scalars().all()
    # Return in chronological order
    return list(reversed(messages))


def _calculate_free_times(events: List[dict]) -> List[str]:
    """
    Calculate free time slots between events.

    This is a simple implementation. Can be enhanced to be smarter.
    """
    if not events:
        return ["You have no scheduled events in the next 2 weeks"]

    free_slots = []
    # Simple logic: find gaps between consecutive events
    for i in range(len(events) - 1):
        current_end = events[i]["end_datetime"]
        next_start = events[i + 1]["start_datetime"]

        # If there's a gap of more than 1 hour, it's free time
        if current_end and next_start:
            try:
                end_dt = datetime.fromisoformat(current_end.replace("Z", "+00:00"))
                start_dt = datetime.fromisoformat(next_start.replace("Z", "+00:00"))
                gap = start_dt - end_dt

                if gap.total_seconds() > 3600:  # More than 1 hour
                    free_slots.append(
                        f"{end_dt.strftime('%a %b %d, %I:%M%p')} to {start_dt.strftime('%I:%M%p')}"
                    )
            except (ValueError, AttributeError):
                pass

    return free_slots[:5]  # Return top 5 free slots
