"""Event service with business logic."""
from datetime import datetime
from typing import Optional, Tuple
from math import ceil

from sqlalchemy import and_, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api.errors import ConflictError, NotFoundError
from app.models.event import Event, EventCreate, EventUpdate


class EventService:
    """Service class for event operations."""

    @staticmethod
    async def create_event(
        session: AsyncSession,
        event_data: EventCreate,
    ) -> Event:
        """Create a new event."""
        # Check for overlap if all_day is True
        if event_data.all_day:
            await EventService._check_all_day_overlap(
                session, event_data.start_datetime, event_data.end_datetime
            )

        # Convert to UTC for storage
        event = Event.model_validate(event_data.model_dump())
        event.updated_at = datetime.utcnow()

        session.add(event)
        await session.commit()
        await session.refresh(event)
        return event

    @staticmethod
    async def get_event(session: AsyncSession, event_id: int) -> Event:
        """Get event by ID."""
        statement = select(Event).where(Event.id == event_id)
        result = await session.exec(statement)
        event = result.first()
        if not event:
            raise NotFoundError(f"Event with id {event_id} not found")
        return event

    @staticmethod
    async def list_events(
        session: AsyncSession,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        query: Optional[str] = None,
        page: int = 1,
        size: int = 20,
    ) -> Tuple[list[Event], int]:
        """List events with filtering and pagination."""
        statement = select(Event)

        # Apply filters
        filters = []

        if from_date:
            filters.append(Event.start_datetime >= from_date)

        if to_date:
            filters.append(Event.end_datetime <= to_date)

        if query:
            search_filter = or_(
                Event.title.ilike(f"%{query}%"),
                Event.description.ilike(f"%{query}%"),
                Event.location.ilike(f"%{query}%"),
            )
            filters.append(search_filter)

        if filters:
            statement = statement.where(and_(*filters))

        # Get total count
        count_statement = select(func.count()).select_from(statement.subquery())
        total_result = await session.exec(count_statement)
        total = total_result.first() or 0

        # Apply pagination
        offset = (page - 1) * size
        statement = statement.offset(offset).limit(size)

        # Order by start date
        statement = statement.order_by(Event.start_datetime)

        result = await session.exec(statement)
        events = result.all()

        return events, total

    @staticmethod
    async def update_event(
        session: AsyncSession,
        event_id: int,
        event_data: EventUpdate,
    ) -> Event:
        """Update an existing event."""
        event = await EventService.get_event(session, event_id)

        # Get update data, filtering out None values
        update_data = event_data.model_dump(exclude_unset=True, exclude_none=True)

        if not update_data:
            return event

        # Validate datetime logic if both start and end are being updated
        start_dt = update_data.get("start_datetime", event.start_datetime)
        end_dt = update_data.get("end_datetime", event.end_datetime)

        if end_dt <= start_dt:
            raise ConflictError("End datetime must be after start datetime")

        # Check for all-day overlap if relevant
        all_day = update_data.get("all_day", event.all_day)
        if all_day:
            await EventService._check_all_day_overlap(
                session, start_dt, end_dt, exclude_event_id=event_id
            )

        # Apply updates
        for field, value in update_data.items():
            setattr(event, field, value)

        event.updated_at = datetime.utcnow()

        await session.commit()
        await session.refresh(event)
        return event

    @staticmethod
    async def delete_event(session: AsyncSession, event_id: int) -> None:
        """Delete an event."""
        event = await EventService.get_event(session, event_id)
        await session.delete(event)
        await session.commit()

    @staticmethod
    async def _check_all_day_overlap(
        session: AsyncSession,
        start_datetime: datetime,
        end_datetime: datetime,
        exclude_event_id: Optional[int] = None,
    ) -> None:
        """Check for overlapping all-day events."""
        statement = select(Event).where(
            Event.all_day.is_(True),
            or_(
                and_(
                    Event.start_datetime <= start_datetime,
                    Event.end_datetime > start_datetime,
                ),
                and_(
                    Event.start_datetime < end_datetime,
                    Event.end_datetime >= end_datetime,
                ),
                and_(
                    Event.start_datetime >= start_datetime,
                    Event.end_datetime <= end_datetime,
                ),
            ),
        )

        if exclude_event_id:
            statement = statement.where(Event.id != exclude_event_id)

        result = await session.exec(statement)
        overlapping_event = result.first()

        if overlapping_event:
            raise ConflictError(
                f"All-day event overlaps with existing event: {overlapping_event.title}"
            )