"""Simple server to test the basic functionality"""
import json
import sqlite3
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="AI Calendar Backend", version="0.1.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple Pydantic models
class EventBase(BaseModel):
    title: str
    description: str | None = None
    start_datetime: datetime
    end_datetime: datetime
    all_day: bool = False
    location: str | None = None
    attendees: list[str] = []
    original_timezone: str = "UTC"

class EventCreate(EventBase):
    pass

class Event(EventBase):
    id: int
    created_at: datetime
    updated_at: datetime

class EventListResponse(BaseModel):
    events: list[Event]
    total: int
    page: int
    size: int
    pages: int

# Database setup
def init_db():
    conn = sqlite3.connect("data/simple_app.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            start_datetime TEXT NOT NULL,
            end_datetime TEXT NOT NULL,
            all_day INTEGER NOT NULL DEFAULT 0,
            location TEXT,
            attendees TEXT DEFAULT '[]',
            original_timezone TEXT DEFAULT 'UTC',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

@app.on_event("startup")
async def startup_event():
    init_db()

@app.get("/healthz")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/v1/events", response_model=EventListResponse)
async def list_events(page: int = 1, size: int = 20):
    conn = sqlite3.connect("data/simple_app.db")
    cursor = conn.cursor()

    # Get total count
    cursor.execute("SELECT COUNT(*) FROM events")
    total = cursor.fetchone()[0]

    # Get events with pagination
    offset = (page - 1) * size
    cursor.execute("""
        SELECT id, title, description, start_datetime, end_datetime, all_day,
               location, attendees, original_timezone, created_at, updated_at
        FROM events
        ORDER BY start_datetime
        LIMIT ? OFFSET ?
    """, (size, offset))

    events = []
    for row in cursor.fetchall():
        event_dict = {
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "start_datetime": row[3],
            "end_datetime": row[4],
            "all_day": bool(row[5]),
            "location": row[6],
            "attendees": json.loads(row[7] or '[]'),
            "original_timezone": row[8],
            "created_at": row[9],
            "updated_at": row[10],
        }
        events.append(Event(**event_dict))

    conn.close()

    pages = (total + size - 1) // size
    return EventListResponse(
        events=events,
        total=total,
        page=page,
        size=size,
        pages=pages
    )

@app.post("/api/v1/events", response_model=Event, status_code=201)
async def create_event(event_data: EventCreate):
    now = datetime.utcnow().isoformat()

    conn = sqlite3.connect("data/simple_app.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO events (title, description, start_datetime, end_datetime, all_day,
                          location, attendees, original_timezone, created_at,
                          updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        event_data.title,
        event_data.description,
        event_data.start_datetime.isoformat(),
        event_data.end_datetime.isoformat(),
        int(event_data.all_day),
        event_data.location,
        json.dumps(event_data.attendees),
        event_data.original_timezone,
        now,
        now
    ))

    event_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # Return the created event
    return Event(
        id=event_id,
        title=event_data.title,
        description=event_data.description,
        start_datetime=event_data.start_datetime,
        end_datetime=event_data.end_datetime,
        all_day=event_data.all_day,
        location=event_data.location,
        attendees=event_data.attendees,
        original_timezone=event_data.original_timezone,
        created_at=datetime.fromisoformat(now),
        updated_at=datetime.fromisoformat(now)
    )

@app.get("/api/v1/events/{event_id}", response_model=Event)
async def get_event(event_id: int):
    conn = sqlite3.connect("data/simple_app.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, description, start_datetime, end_datetime, all_day,
               location, attendees, original_timezone, created_at, updated_at
        FROM events WHERE id = ?
    """, (event_id,))

    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Event not found")

    event_dict = {
        "id": row[0],
        "title": row[1],
        "description": row[2],
        "start_datetime": row[3],
        "end_datetime": row[4],
        "all_day": bool(row[5]),
        "location": row[6],
        "attendees": json.loads(row[7] or '[]'),
        "original_timezone": row[8],
        "created_at": row[9],
        "updated_at": row[10],
    }

    conn.close()
    return Event(**event_dict)

# LLM-powered AI draft endpoint
@app.post("/api/v1/events/draft")
async def create_event_draft(prompt_data: dict):
    prompt = prompt_data.get("prompt", "")

    if not prompt:
        return {
            "title": "New Event",
            "description": "",
            "start_datetime": None,
            "end_datetime": None,
            "all_day": False,
            "location": None,
            "attendees": [],
            "confidence": 0.0,
            "extracted_entities": {"error": "No prompt provided"}
        }

    # Use LLM-powered extraction
    try:
        from llm_event_extractor import LLMEventExtractor

        extractor = LLMEventExtractor()
        result = extractor.extract_event_data(prompt)

        return {
            "title": result.title,
            "description": result.description,
            "start_datetime": result.start_datetime,
            "end_datetime": result.end_datetime,
            "all_day": result.all_day,
            "location": result.location,
            "attendees": result.attendees,
            "confidence": result.confidence,
            "extracted_entities": {
                "prompt": prompt,
                "reasoning": result.reasoning,
                "extraction_method": "llm" if result.confidence > 0.5 else "rule-based"
            }
        }
    except Exception as e:
        # Fallback to simple rule-based extraction on any error
        import re

        title = "New Event"
        if "meeting" in prompt.lower():
            title = "Meeting"
        elif "lunch" in prompt.lower():
            title = "Lunch"
        elif "call" in prompt.lower():
            title = "Call"

        # Extract people
        with_match = re.search(r'with\s+(\w+)', prompt, re.IGNORECASE)
        if with_match:
            title += f" with {with_match.group(1)}"

        return {
            "title": title,
            "description": prompt,
            "start_datetime": None,
            "end_datetime": None,
            "all_day": False,
            "location": None,
            "attendees": [],
            "confidence": 0.3,
            "extracted_entities": {
                "prompt": prompt,
                "error": str(e),
                "extraction_method": "rule-based-fallback"
            }
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
