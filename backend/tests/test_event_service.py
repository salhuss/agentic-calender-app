"""Test event service business logic."""

from datetime import datetime, timedelta
from typing import Any

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.errors import ConflictError, NotFoundError
from app.models.event import EventCreate, EventUpdate
from app.services.event_service import EventService


@pytest.mark.asyncio
async def test_create_event(test_session: AsyncSession) -> None:
    """Test creating a regular event."""
    event_data = EventCreate(
        title="Test Event",
        description="Test Description",
        start_datetime=datetime(2024, 1, 1, 10, 0),
        end_datetime=datetime(2024, 1, 1, 11, 0),
        all_day=False,
        location="Test Location",
        attendees=["test@example.com"],
        original_timezone="UTC"
    )

    event = await EventService.create_event(test_session, event_data)

    assert event.title == "Test Event"
    assert event.description == "Test Description"
    assert event.all_day is False
    assert event.location == "Test Location"
    assert event.attendees == ["test@example.com"]
    assert event.id is not None


@pytest.mark.asyncio
async def test_create_all_day_event(test_session: AsyncSession) -> None:
    """Test creating an all-day event."""
    event_data = EventCreate(
        title="All Day Event",
        description="All Day Description",
        start_datetime=datetime(2024, 1, 1, 0, 0),
        end_datetime=datetime(2024, 1, 1, 23, 59),
        all_day=True,
        location="Everywhere",
        attendees=[],
        original_timezone="UTC"
    )

    event = await EventService.create_event(test_session, event_data)

    assert event.title == "All Day Event"
    assert event.all_day is True


@pytest.mark.asyncio
async def test_create_all_day_event_with_overlap(test_session: AsyncSession) -> None:
    """Test creating overlapping all-day events raises ConflictError."""
    # Create first all-day event
    first_event = EventCreate(
        title="First All Day Event",
        start_datetime=datetime(2024, 1, 1, 0, 0),
        end_datetime=datetime(2024, 1, 1, 23, 59),
        all_day=True,
    )
    await EventService.create_event(test_session, first_event)

    # Try to create overlapping all-day event
    overlapping_event = EventCreate(
        title="Overlapping All Day Event",
        start_datetime=datetime(2024, 1, 1, 0, 0),
        end_datetime=datetime(2024, 1, 1, 23, 59),
        all_day=True,
    )

    with pytest.raises(ConflictError, match="All-day event overlaps with existing event"):
        await EventService.create_event(test_session, overlapping_event)


@pytest.mark.asyncio
async def test_get_event_success(test_session: AsyncSession) -> None:
    """Test getting an event by ID."""
    # Create an event first
    event_data = EventCreate(
        title="Test Event",
        start_datetime=datetime(2024, 1, 1, 10, 0),
        end_datetime=datetime(2024, 1, 1, 11, 0),
        all_day=False
    )
    created_event = await EventService.create_event(test_session, event_data)

    # Get the event
    retrieved_event = await EventService.get_event(test_session, created_event.id)

    assert retrieved_event.id == created_event.id
    assert retrieved_event.title == "Test Event"


@pytest.mark.asyncio
async def test_get_event_not_found(test_session: AsyncSession) -> None:
    """Test getting non-existent event raises NotFoundError."""
    with pytest.raises(NotFoundError, match="Event with id 999 not found"):
        await EventService.get_event(test_session, 999)


@pytest.mark.asyncio
async def test_list_events_no_filters(test_session: AsyncSession) -> None:
    """Test listing events without filters."""
    # Create test events
    event1_data = EventCreate(
        title="Event 1",
        start_datetime=datetime(2024, 1, 1, 10, 0),
        end_datetime=datetime(2024, 1, 1, 11, 0)
    )
    event2_data = EventCreate(
        title="Event 2",
        start_datetime=datetime(2024, 1, 2, 10, 0),
        end_datetime=datetime(2024, 1, 2, 11, 0)
    )
    await EventService.create_event(test_session, event1_data)
    await EventService.create_event(test_session, event2_data)

    events, total = await EventService.list_events(test_session)

    assert len(events) == 2
    assert total == 2
    assert events[0].title == "Event 1"  # Ordered by start_datetime


@pytest.mark.asyncio
async def test_list_events_with_date_filter(test_session: AsyncSession) -> None:
    """Test listing events with date filters."""
    # Create events on different dates
    early_event = EventCreate(
        title="Early Event",
        start_datetime=datetime(2024, 1, 1, 10, 0),
        end_datetime=datetime(2024, 1, 1, 11, 0)
    )
    late_event = EventCreate(
        title="Late Event",
        start_datetime=datetime(2024, 1, 10, 10, 0),
        end_datetime=datetime(2024, 1, 10, 11, 0)
    )
    await EventService.create_event(test_session, early_event)
    await EventService.create_event(test_session, late_event)

    # Filter from Jan 5 onwards
    events, total = await EventService.list_events(
        test_session,
        from_date=datetime(2024, 1, 5)
    )

    assert len(events) == 1
    assert total == 1
    assert events[0].title == "Late Event"

    # Filter up to Jan 5
    events, total = await EventService.list_events(
        test_session,
        to_date=datetime(2024, 1, 5)
    )

    assert len(events) == 1
    assert events[0].title == "Early Event"


@pytest.mark.asyncio
async def test_list_events_with_search_query(test_session: AsyncSession) -> None:
    """Test listing events with search query."""
    # Create events with different content
    event1 = EventCreate(
        title="Meeting with John",
        description="Discuss project",
        location="Office",
        start_datetime=datetime(2024, 1, 1, 10, 0),
        end_datetime=datetime(2024, 1, 1, 11, 0)
    )
    event2 = EventCreate(
        title="Lunch break",
        description="Eat at cafe",
        location="Cafe Rio",
        start_datetime=datetime(2024, 1, 1, 12, 0),
        end_datetime=datetime(2024, 1, 1, 13, 0)
    )
    await EventService.create_event(test_session, event1)
    await EventService.create_event(test_session, event2)

    # Search by title
    events, total = await EventService.list_events(test_session, query="meeting")
    assert len(events) == 1
    assert events[0].title == "Meeting with John"

    # Search by description
    events, total = await EventService.list_events(test_session, query="cafe")
    assert len(events) == 1
    assert events[0].title == "Lunch break"

    # Search by location
    events, total = await EventService.list_events(test_session, query="office")
    assert len(events) == 1
    assert events[0].title == "Meeting with John"


@pytest.mark.asyncio
async def test_list_events_pagination(test_session: AsyncSession) -> None:
    """Test event listing pagination."""
    # Create multiple events
    for i in range(5):
        event_data = EventCreate(
            title=f"Event {i}",
            start_datetime=datetime(2024, 1, i+1, 10, 0),
            end_datetime=datetime(2024, 1, i+1, 11, 0)
        )
        await EventService.create_event(test_session, event_data)

    # Test pagination
    events, total = await EventService.list_events(test_session, page=1, size=2)
    assert len(events) == 2
    assert total == 5

    events, total = await EventService.list_events(test_session, page=2, size=2)
    assert len(events) == 2
    assert events[0].title == "Event 2"  # Ordered by start_datetime


@pytest.mark.asyncio
async def test_update_event(test_session: AsyncSession) -> None:
    """Test updating an event."""
    # Create event
    event_data = EventCreate(
        title="Original Event",
        description="Original Description",
        start_datetime=datetime(2024, 1, 1, 10, 0),
        end_datetime=datetime(2024, 1, 1, 11, 0)
    )
    created_event = await EventService.create_event(test_session, event_data)

    # Update event
    update_data = EventUpdate(
        title="Updated Event",
        description="Updated Description"
    )
    updated_event = await EventService.update_event(
        test_session, created_event.id, update_data
    )

    assert updated_event.title == "Updated Event"
    assert updated_event.description == "Updated Description"


@pytest.mark.asyncio
async def test_update_event_no_changes(test_session: AsyncSession) -> None:
    """Test updating event with no changes."""
    # Create event
    event_data = EventCreate(
        title="Test Event",
        start_datetime=datetime(2024, 1, 1, 10, 0),
        end_datetime=datetime(2024, 1, 1, 11, 0)
    )
    created_event = await EventService.create_event(test_session, event_data)

    # Update with no data
    update_data = EventUpdate()
    updated_event = await EventService.update_event(
        test_session, created_event.id, update_data
    )

    # Should return the same event unchanged
    assert updated_event.id == created_event.id
    assert updated_event.title == created_event.title


@pytest.mark.asyncio
async def test_update_event_invalid_datetime(test_session: AsyncSession) -> None:
    """Test updating event with invalid datetime raises ConflictError."""
    # Create event
    event_data = EventCreate(
        title="Test Event",
        start_datetime=datetime(2024, 1, 1, 10, 0),
        end_datetime=datetime(2024, 1, 1, 11, 0)
    )
    created_event = await EventService.create_event(test_session, event_data)

    # Try to update with end before start
    update_data = EventUpdate(
        start_datetime=datetime(2024, 1, 1, 12, 0),
        end_datetime=datetime(2024, 1, 1, 10, 0)  # Before start
    )

    with pytest.raises(ConflictError, match="End datetime must be after start datetime"):
        await EventService.update_event(test_session, created_event.id, update_data)


@pytest.mark.asyncio
async def test_update_all_day_event_with_overlap(test_session: AsyncSession) -> None:
    """Test updating to all-day event with overlap raises ConflictError."""
    # Create first all-day event
    all_day_event = EventCreate(
        title="Existing All Day Event",
        start_datetime=datetime(2024, 1, 1, 0, 0),
        end_datetime=datetime(2024, 1, 1, 23, 59),
        all_day=True
    )
    await EventService.create_event(test_session, all_day_event)

    # Create regular event
    regular_event = EventCreate(
        title="Regular Event",
        start_datetime=datetime(2024, 1, 2, 10, 0),
        end_datetime=datetime(2024, 1, 2, 11, 0),
        all_day=False
    )
    created_event = await EventService.create_event(test_session, regular_event)

    # Try to update regular event to overlap with all-day event
    update_data = EventUpdate(
        start_datetime=datetime(2024, 1, 1, 10, 0),
        end_datetime=datetime(2024, 1, 1, 11, 0),
        all_day=True
    )

    with pytest.raises(ConflictError, match="All-day event overlaps with existing event"):
        await EventService.update_event(test_session, created_event.id, update_data)


@pytest.mark.asyncio
async def test_delete_event(test_session: AsyncSession) -> None:
    """Test deleting an event."""
    # Create event
    event_data = EventCreate(
        title="To Be Deleted",
        start_datetime=datetime(2024, 1, 1, 10, 0),
        end_datetime=datetime(2024, 1, 1, 11, 0)
    )
    created_event = await EventService.create_event(test_session, event_data)

    # Delete event
    await EventService.delete_event(test_session, created_event.id)

    # Verify event is deleted
    with pytest.raises(NotFoundError):
        await EventService.get_event(test_session, created_event.id)


@pytest.mark.asyncio
async def test_delete_nonexistent_event(test_session: AsyncSession) -> None:
    """Test deleting non-existent event raises NotFoundError."""
    with pytest.raises(NotFoundError, match="Event with id 999 not found"):
        await EventService.delete_event(test_session, 999)


@pytest.mark.asyncio
async def test_check_all_day_overlap_with_exclude_id(test_session: AsyncSession) -> None:
    """Test all-day overlap check excludes specified event ID."""
    # Create all-day event
    event_data = EventCreate(
        title="All Day Event",
        start_datetime=datetime(2024, 1, 1, 0, 0),
        end_datetime=datetime(2024, 1, 1, 23, 59),
        all_day=True
    )
    created_event = await EventService.create_event(test_session, event_data)

    # Check overlap excluding the same event (should not raise error)
    await EventService._check_all_day_overlap(
        test_session,
        datetime(2024, 1, 1, 0, 0),
        datetime(2024, 1, 1, 23, 59),
        exclude_event_id=created_event.id
    )

    # This should complete without raising ConflictError
    assert True