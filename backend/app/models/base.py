"""Base model definitions."""
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class TimestampMixin(SQLModel):
    """Mixin to add created_at and updated_at fields."""

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class BaseResponse(SQLModel):
    """Base response model for API responses."""

    id: int
    created_at: datetime
    updated_at: datetime