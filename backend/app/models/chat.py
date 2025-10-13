"""Chat models."""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class ChatMessage(SQLModel, table=True):
    """Chat message model."""

    __tablename__ = "chat_messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    role: str = Field(
        index=True, description="Message role: 'user' or 'assistant'"
    )  # user or assistant
    content: str = Field(description="Message content")
    context: Optional[str] = Field(
        default=None, description="JSON string of context data provided to LLM"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    # Future: Add user_id for multi-user support
    # user_id: Optional[int] = Field(default=None, foreign_key="users.id")


class ChatMessageCreate(SQLModel):
    """Schema for creating a chat message."""

    message: str = Field(description="User message content")


class ChatMessageResponse(SQLModel):
    """Schema for chat message response."""

    id: int
    role: str
    content: str
    created_at: datetime


class ChatResponse(SQLModel):
    """Schema for chat API response."""

    response: str = Field(description="Assistant response")
    message_id: int = Field(description="ID of the saved assistant message")
