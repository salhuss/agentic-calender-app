"""Test events API endpoints."""

from typing import Any

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_event(
    client: AsyncClient, sample_event_data: dict[str, Any]
) -> None:
    """Test creating an event."""
    response = await client.post("/api/v1/events/", json=sample_event_data)
    assert response.status_code == 201

    data = response.json()
    assert data["title"] == sample_event_data["title"]
    assert data["description"] == sample_event_data["description"]
    assert data["all_day"] == sample_event_data["all_day"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_create_event_invalid_datetime(
    client: AsyncClient, sample_event_data: dict[str, Any]
) -> None:
    """Test creating an event with invalid datetime (end before start)."""
    invalid_data = sample_event_data.copy()
    invalid_data["start_datetime"] = "2023-12-01T12:00:00Z"
    invalid_data["end_datetime"] = "2023-12-01T10:00:00Z"

    response = await client.post("/api/v1/events/", json=invalid_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_event(
    client: AsyncClient, sample_event_data: dict[str, Any]
) -> None:
    """Test getting a specific event."""
    # Create event first
    create_response = await client.post("/api/v1/events/", json=sample_event_data)
    event_id = create_response.json()["id"]

    # Get the event
    response = await client.get(f"/api/v1/events/{event_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == event_id
    assert data["title"] == sample_event_data["title"]


@pytest.mark.asyncio
async def test_get_nonexistent_event(client: AsyncClient) -> None:
    """Test getting a non-existent event."""
    response = await client.get("/api/v1/events/999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_events(
    client: AsyncClient, sample_event_data: dict[str, Any]
) -> None:
    """Test listing events."""
    # Create a few events
    for i in range(3):
        event_data = sample_event_data.copy()
        event_data["title"] = f"Test Event {i + 1}"
        await client.post("/api/v1/events/", json=event_data)

    # List events
    response = await client.get("/api/v1/events/")
    assert response.status_code == 200

    data = response.json()
    assert "events" in data
    assert "total" in data
    assert "page" in data
    assert "size" in data
    assert "pages" in data
    assert len(data["events"]) == 3
    assert data["total"] == 3


@pytest.mark.asyncio
async def test_list_events_with_query(
    client: AsyncClient, sample_event_data: dict[str, Any]
) -> None:
    """Test listing events with search query."""
    # Create events with different titles
    event1 = sample_event_data.copy()
    event1["title"] = "Important Meeting"
    await client.post("/api/v1/events/", json=event1)

    event2 = sample_event_data.copy()
    event2["title"] = "Casual Coffee"
    await client.post("/api/v1/events/", json=event2)

    # Search for 'meeting'
    response = await client.get("/api/v1/events/?query=meeting")
    assert response.status_code == 200

    data = response.json()
    assert len(data["events"]) == 1
    assert data["events"][0]["title"] == "Important Meeting"


@pytest.mark.asyncio
async def test_update_event(
    client: AsyncClient, sample_event_data: dict[str, Any]
) -> None:
    """Test updating an event."""
    # Create event
    create_response = await client.post("/api/v1/events/", json=sample_event_data)
    event_id = create_response.json()["id"]

    # Update event
    update_data = {"title": "Updated Event", "description": "Updated description"}
    response = await client.put(f"/api/v1/events/{event_id}", json=update_data)
    assert response.status_code == 200

    data = response.json()
    assert data["title"] == "Updated Event"
    assert data["description"] == "Updated description"
    # Other fields should remain unchanged
    assert data["location"] == sample_event_data["location"]


@pytest.mark.asyncio
async def test_delete_event(
    client: AsyncClient, sample_event_data: dict[str, Any]
) -> None:
    """Test deleting an event."""
    # Create event
    create_response = await client.post("/api/v1/events/", json=sample_event_data)
    event_id = create_response.json()["id"]

    # Delete event
    response = await client.delete(f"/api/v1/events/{event_id}")
    assert response.status_code == 204

    # Verify event is gone
    get_response = await client.get(f"/api/v1/events/{event_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_all_day_event_overlap_prevention(client: AsyncClient) -> None:
    """Test that overlapping all-day events are prevented."""
    # Create first all-day event
    event1 = {
        "title": "All Day Event 1",
        "start_datetime": "2023-12-01T00:00:00Z",
        "end_datetime": "2023-12-01T23:59:59Z",
        "all_day": True,
    }
    response1 = await client.post("/api/v1/events/", json=event1)
    assert response1.status_code == 201

    # Try to create overlapping all-day event
    event2 = {
        "title": "All Day Event 2",
        "start_datetime": "2023-12-01T00:00:00Z",
        "end_datetime": "2023-12-01T23:59:59Z",
        "all_day": True,
    }
    response2 = await client.post("/api/v1/events/", json=event2)
    assert response2.status_code == 409  # Conflict


@pytest.mark.asyncio
async def test_timed_events_can_overlap(client: AsyncClient) -> None:
    """Test that timed events can overlap (as per requirements)."""
    # Create first timed event
    event1 = {
        "title": "Meeting 1",
        "start_datetime": "2023-12-01T10:00:00Z",
        "end_datetime": "2023-12-01T11:00:00Z",
        "all_day": False,
    }
    response1 = await client.post("/api/v1/events/", json=event1)
    assert response1.status_code == 201

    # Create overlapping timed event (should be allowed)
    event2 = {
        "title": "Meeting 2",
        "start_datetime": "2023-12-01T10:30:00Z",
        "end_datetime": "2023-12-01T11:30:00Z",
        "all_day": False,
    }
    response2 = await client.post("/api/v1/events/", json=event2)
    assert response2.status_code == 201


@pytest.mark.asyncio
async def test_create_event_draft(client: AsyncClient) -> None:
    """Test creating an event draft from natural language."""
    response = await client.post(
        "/api/v1/events/draft", json={"prompt": "Meeting with John tomorrow at 3pm"}
    )
    assert response.status_code == 200

    data = response.json()
    assert "title" in data
    assert "confidence" in data
    assert "extracted_entities" in data
    assert isinstance(data["confidence"], float)
    assert 0.0 <= data["confidence"] <= 1.0


@pytest.mark.asyncio
async def test_list_events_empty_database(client: AsyncClient) -> None:
    """Test listing events when database is empty (line 43: else 1 case)."""
    response = await client.get("/api/v1/events/")
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 0
    assert data["pages"] == 1  # This should hit the 'else 1' case on line 43
    assert len(data["events"]) == 0


@pytest.mark.asyncio
async def test_create_event_draft_missing_prompt(client: AsyncClient) -> None:
    """Test creating an event draft without a prompt."""
    response = await client.post("/api/v1/events/draft", json={})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_event_with_invalid_email(client: AsyncClient) -> None:
    """Test creating an event with invalid attendee email."""
    event_data = {
        "title": "Test Event",
        "start_datetime": "2023-12-01T10:00:00Z",
        "end_datetime": "2023-12-01T11:00:00Z",
        "attendees": ["invalid-email"],
    }
    response = await client.post("/api/v1/events/", json=event_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_event_with_invalid_email(client: AsyncClient) -> None:
    """Test updating an event with invalid attendee email."""
    # Create event first
    event_data = {
        "title": "Test Event",
        "start_datetime": "2023-12-01T10:00:00Z",
        "end_datetime": "2023-12-01T11:00:00Z",
    }
    create_response = await client.post("/api/v1/events/", json=event_data)
    event_id = create_response.json()["id"]

    # Try to update with invalid email
    update_data = {"attendees": ["not-an-email"]}
    response = await client.put(f"/api/v1/events/{event_id}", json=update_data)
    assert response.status_code == 422
