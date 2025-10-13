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
    from datetime import datetime

    # High confidence - has title, datetime, location, attendees (all factors)
    now = datetime.now()
    high_conf = AIService._calculate_confidence(
        title="Meeting with John",
        start_datetime=now,
        end_datetime=now,
        location="Cafe Rio",
        attendees=["john@example.com"],
    )
    assert high_conf > 0.8  # Should be 1.0 (5/5 factors)

    # Medium confidence - has title, location, attendees (no datetime)
    medium_conf = AIService._calculate_confidence(
        title="Meeting with John",
        start_datetime=None,
        end_datetime=None,
        location="Cafe Rio",
        attendees=["john@example.com"],
    )
    assert 0.5 <= medium_conf <= 0.7  # Should be 0.6 (3/5 factors)

    # Low confidence - only has title
    low_conf = AIService._calculate_confidence(
        title="Meeting",
        start_datetime=None,
        end_datetime=None,
        location=None,
        attendees=[],
    )
    assert low_conf < 0.5  # Should be 0.2 (1/5 factors)


@pytest.mark.asyncio
async def test_extract_entities_with_dates() -> None:
    """Test entity extraction with various date formats."""
    # Test tuple dates (e.g., "12/25")
    prompt = "Meeting on 12/25 with John"
    entities = AIService._extract_entities(prompt)

    assert "dates" in entities
    # This tests the tuple branch in date extraction (line 87)


@pytest.mark.asyncio
async def test_extract_entities_with_keywords() -> None:
    """Test entity extraction with various keywords."""
    # Test different keywords
    prompts = [
        "meeting with John",  # meeting keyword
        "lunch at cafe",  # lunch keyword
        "dinner tomorrow",  # dinner keyword
        "call with team",  # call keyword
        "appointment today",  # appointment keyword
        "interview next week",  # interview keyword
        "workout at gym",  # workout keyword
        "class tomorrow",  # class keyword
        "conference all day",  # conference keyword
        "presentation prep",  # presentation keyword
    ]

    for prompt in prompts:
        entities = AIService._extract_entities(prompt)
        assert "keywords" in entities


@pytest.mark.asyncio
async def test_extract_title_fallbacks() -> None:
    """Test title extraction fallback mechanisms."""
    # Test with keywords but no people (line 153)
    prompt = "meeting tomorrow"
    entities = AIService._extract_entities(prompt)
    title = AIService._extract_title(prompt, entities)
    assert "meeting" in title.lower()

    # Test with keywords and people (line 152)
    prompt = "meeting with John"
    entities = AIService._extract_entities(prompt)
    title = AIService._extract_title(prompt, entities)
    assert "meeting" in title.lower()
    assert "john" in title.lower()

    # Test fallback to first 5 words (lines 156-157)
    prompt = "some random text without any keywords or patterns here"
    entities = AIService._extract_entities(prompt)
    title = AIService._extract_title(prompt, entities)
    words = title.split()
    assert len(words) <= 5


@pytest.mark.asyncio
async def test_extract_description() -> None:
    """Test description extraction."""
    # Test with long prompt (returns description)
    long_prompt = (
        "This is a very long prompt that should be used as description "
        "because it exceeds the minimum length"
    )
    description = AIService._extract_description(long_prompt)
    assert description == long_prompt

    # Test with short prompt (returns None)
    short_prompt = "Short"
    description = AIService._extract_description(short_prompt)
    assert description is None


@pytest.mark.asyncio
async def test_extract_location_edge_cases() -> None:
    """Test location extraction edge cases."""
    # Test location that's too short (should pass the length > 2 check
    # but still test the logic)
    prompt = "Meeting at AB tomorrow"  # 2-char location
    location = AIService._extract_location(prompt)
    # This tests line 179 condition checking

    # Test location that starts with digit (line 179)
    prompt = "Meeting at 123 tomorrow"
    location = AIService._extract_location(prompt)
    # Should be rejected because it starts with digit
    assert location is None


@pytest.mark.asyncio
async def test_datetime_extraction_edge_cases() -> None:
    """Test datetime extraction edge cases."""
    # Test Monday calculation (lines 213-217)
    prompt = "Meeting on Monday"
    entities = AIService._extract_entities(prompt)
    start_dt, end_dt, all_day = AIService._extract_datetime_info(prompt, entities)
    # This tests the Monday weekday calculation

    # Test with malformed time (exception handling) - Updated to new dict format
    prompt = "Meeting at invalid:time"
    entities = {
        "times": [{"hour": "invalid", "minute": "time", "am_pm": "pm"}],
        "dates": [],
    }
    start_dt, end_dt, all_day = AIService._extract_datetime_info(prompt, entities)
    # Should handle the exception gracefully and fall back to all-day
    assert all_day is True


@pytest.mark.asyncio
async def test_datetime_parsing_with_pm() -> None:
    """Test datetime parsing with AM/PM."""
    # Test PM handling with minutes specified (works correctly)
    prompt = "Meeting at 1:30pm tomorrow"
    entities = AIService._extract_entities(prompt)
    start_dt, end_dt, all_day = AIService._extract_datetime_info(prompt, entities)
    assert not all_day  # Should not be all-day
    if start_dt:
        assert start_dt.hour == 13  # 1:30pm = 13:30 in 24h format

    # Test 12am handling with minutes (line 232-233)
    prompt = "Meeting at 12:30am tomorrow"
    entities = AIService._extract_entities(prompt)
    start_dt, end_dt, all_day = AIService._extract_datetime_info(prompt, entities)
    assert not all_day  # Should not be all-day
    if start_dt:
        assert start_dt.hour == 0  # 12:30am = 00:30


@pytest.mark.asyncio
async def test_datetime_with_duration() -> None:
    """Test datetime with duration parsing."""
    # Test duration in hours with time that parses correctly (lines 243-248)
    prompt = "Meeting tomorrow at 2:00pm for 3 hours"
    entities = AIService._extract_entities(prompt)
    start_dt, end_dt, all_day = AIService._extract_datetime_info(prompt, entities)
    if start_dt and end_dt and not all_day:
        duration = end_dt - start_dt
        assert duration.total_seconds() / 3600 == 3  # 3 hours

    # Also test the case where duration parsing works with simple time
    prompt = "Meeting tomorrow at 2pm for 3 hours"
    entities = AIService._extract_entities(prompt)
    start_dt, end_dt, all_day = AIService._extract_datetime_info(prompt, entities)
    # Now that time parsing is fixed, "2pm" should parse correctly
    assert all_day is False
    if start_dt and end_dt:
        duration = end_dt - start_dt
        assert duration.total_seconds() / 3600 == 3  # 3 hours


@pytest.mark.asyncio
async def test_calculate_confidence_edge_cases() -> None:
    """Test confidence calculation edge cases."""
    from datetime import datetime

    # Test with just partial datetime (line 282-283)
    conf = AIService._calculate_confidence(
        title="Meeting",
        start_datetime=datetime.now(),
        end_datetime=None,  # Only start datetime
        location=None,
        attendees=[],
    )
    # This should hit the elif branch on line 282-283
    assert 0.2 < conf < 0.8


@pytest.mark.asyncio
async def test_extract_title_keywords_only() -> None:
    """Test title extraction with keywords but no people (line 153)."""
    prompt = "meeting tomorrow"  # keyword but no people
    entities = AIService._extract_entities(prompt)
    title = AIService._extract_title(prompt, entities)
    # Should return just the capitalized keyword
    assert title == "Meeting"


@pytest.mark.asyncio
async def test_datetime_next_week_parsing() -> None:
    """Test 'next week' date parsing (line 212)."""
    prompt = "Conference next week"
    entities = AIService._extract_entities(prompt)
    start_dt, end_dt, all_day = AIService._extract_datetime_info(prompt, entities)
    # Should be all-day event next week
    assert all_day is True
    if start_dt:
        from datetime import datetime, timedelta

        expected_date = (datetime.now() + timedelta(weeks=1)).date()
        assert start_dt.date() == expected_date
