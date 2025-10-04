"""Test AI service."""

import pytest

from app.services.ai_service import AIService


@pytest.mark.asyncio
async def test_generate_event_draft_with_time() -> None:
    """Test generating an event draft with time information."""
    prompt = "Meeting with John tomorrow at 3pm"
    draft = await AIService.generate_event_draft(prompt)

    assert draft.title is not None
    assert len(draft.title) > 0
    assert isinstance(draft.confidence, float)
    assert 0.0 <= draft.confidence <= 1.0
    assert isinstance(draft.extracted_entities, dict)


@pytest.mark.asyncio
async def test_generate_event_draft_all_day() -> None:
    """Test generating an all-day event draft."""
    prompt = "Conference all day tomorrow"
    draft = await AIService.generate_event_draft(prompt)

    assert draft.title is not None
    assert draft.all_day is True


@pytest.mark.asyncio
async def test_generate_event_draft_with_location() -> None:
    """Test generating an event draft with location."""
    prompt = "Lunch at Cafe Rio tomorrow 12pm"
    draft = await AIService.generate_event_draft(prompt)

    assert draft.title is not None
    assert draft.location is not None
    assert "cafe" in draft.location.lower() or "rio" in draft.location.lower()


@pytest.mark.asyncio
async def test_generate_event_draft_with_email() -> None:
    """Test generating an event draft with attendee emails."""
    prompt = "Meeting with john@example.com tomorrow at 2pm"
    draft = await AIService.generate_event_draft(prompt)

    assert draft.title is not None
    assert len(draft.attendees) > 0
    assert "john@example.com" in draft.attendees


@pytest.mark.asyncio
async def test_extract_entities() -> None:
    """Test entity extraction."""
    prompt = "Meeting with John at Cafe Rio tomorrow 3pm"
    entities = AIService._extract_entities(prompt)

    assert "times" in entities
    assert "dates" in entities
    assert "locations" in entities
    assert "people" in entities
    assert "keywords" in entities


@pytest.mark.asyncio
async def test_calculate_confidence() -> None:
    """Test confidence calculation."""
    # High confidence - has title, datetime, location, attendees
    high_conf = AIService._calculate_confidence(
        title="Meeting with John",
        start_datetime=None,
        end_datetime=None,
        location="Cafe Rio",
        attendees=["john@example.com"],
    )
    assert high_conf > 0.8

    # Low confidence - only has title
    low_conf = AIService._calculate_confidence(
        title="Meeting",
        start_datetime=None,
        end_datetime=None,
        location=None,
        attendees=[],
    )
    assert low_conf < 0.5
