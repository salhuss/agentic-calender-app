"""Event model and related schemas."""
from datetime import datetime
from typing import Optional

from pydantic import field_validator, model_validator
from sqlalchemy import JSON, UniqueConstraint
from sqlmodel import Field, SQLModel

from app.models.base import TimestampMixin


class EventBase(SQLModel):
    """Base event fields shared across models."""

    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    start_datetime: datetime
    end_datetime: datetime
    all_day: bool = Field(default=False)
    location: Optional[str] = Field(default=None, max_length=500)
    attendees: list[str] = Field(default_factory=list, description="List of email addresses")
    original_timezone: str = Field(default="UTC", max_length=50)

    @field_validator("attendees")
    @classmethod
    def validate_attendees(cls, v: list[str]) -> list[str]:
        """Validate attendee email addresses."""
        import re
        email_regex = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        for email in v:
            if not email_regex.match(email):
                raise ValueError(f"Invalid email address: {email}")
        return v

    @model_validator(mode="after")
    def validate_datetime_logic(self) -> "EventBase":
        """Validate that end_datetime is after start_datetime."""
        if self.end_datetime <= self.start_datetime:
            raise ValueError("End datetime must be after start datetime")
        return self


class Event(EventBase, TimestampMixin, table=True):
    """Event database model."""

    __tablename__ = "events"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Override attendees field with proper JSON type for database
    attendees: list[str] = Field(default_factory=list, sa_column_kwargs={"type_": JSON}, description="List of email addresses")

    # Add unique constraint to prevent identical duplicates (optional requirement)
    __table_args__ = (
        UniqueConstraint(
            "title",
            "start_datetime",
            "end_datetime",
            name="uq_events_title_start_end"
        ),
    )


class EventCreate(EventBase):
    """Schema for creating events."""

    pass


class EventUpdate(SQLModel):
    """Schema for updating events."""

    title: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    all_day: Optional[bool] = None
    location: Optional[str] = Field(default=None, max_length=500)
    attendees: Optional[list[str]] = None
    original_timezone: Optional[str] = Field(default=None, max_length=50)

    @field_validator("attendees")
    @classmethod
    def validate_attendees(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        """Validate attendee email addresses."""
        if v is None:
            return v
        import re
        email_regex = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        for email in v:
            if not email_regex.match(email):
                raise ValueError(f"Invalid email address: {email}")
        return v


class EventResponse(EventBase):
    """Schema for event responses."""

    id: int
    created_at: datetime
    updated_at: datetime


class EventListResponse(SQLModel):
    """Schema for paginated event list responses."""

    events: list[EventResponse]
    total: int
    page: int
    size: int
    pages: int


class EventDraft(SQLModel):
    """Schema for AI-generated event drafts."""

    title: str
    description: Optional[str] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    all_day: bool = Field(default=False)
    location: Optional[str] = None
    attendees: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, description="AI confidence score")
    extracted_entities: dict = Field(default_factory=dict, description="Raw extracted entities")