"""Seed script to populate database with sample data."""
import asyncio
from datetime import datetime, timedelta

from app.core.database import async_session_maker, create_db_and_tables
from app.models.event import Event


async def seed_data() -> None:
    """Create sample events for demonstration purposes."""
    print("Creating database tables...")
    await create_db_and_tables()

    async with async_session_maker() as session:
        # Check if data already exists
        existing_events = await session.get(Event, 1)
        if existing_events:
            print("Sample data already exists. Skipping seed...")
            return

        print("Seeding sample events...")

        # Sample events data
        sample_events = [
            {
                "title": "Team Standup",
                "description": "Daily team standup meeting",
                "start_datetime": datetime.utcnow() + timedelta(
                    days=1, hours=9
                ),
                "end_datetime": datetime.utcnow() + timedelta(
                    days=1, hours=9, minutes=30
                ),
                "all_day": False,
                "location": "Conference Room A",
                "attendees": ["alice@company.com", "bob@company.com"],
                "original_timezone": "UTC",
            },
            {
                "title": "Product Planning Meeting",
                "description": "Quarterly product planning session",
                "start_datetime": datetime.utcnow() + timedelta(
                    days=2, hours=14
                ),
                "end_datetime": datetime.utcnow() + timedelta(
                    days=2, hours=16
                ),
                "all_day": False,
                "location": "Zoom Meeting Room",
                "attendees": [
                    "product@company.com",
                    "engineering@company.com"
                ],
                "original_timezone": "UTC",
            },
            {
                "title": "Company All-Hands",
                "description": "Monthly company-wide meeting",
                "start_datetime": datetime.utcnow() + timedelta(days=3),
                "end_datetime": datetime.utcnow() + timedelta(
                    days=3, hours=23, minutes=59, seconds=59
                ),
                "all_day": True,
                "location": "Main Auditorium",
                "attendees": [],
                "original_timezone": "UTC",
            },
            {
                "title": "Lunch with Client",
                "description": "Business lunch with potential client",
                "start_datetime": datetime.utcnow() + timedelta(
                    days=4, hours=12
                ),
                "end_datetime": datetime.utcnow() + timedelta(
                    days=4, hours=13, minutes=30
                ),
                "all_day": False,
                "location": "Restaurant Downtown",
                "attendees": ["client@example.com"],
                "original_timezone": "UTC",
            },
            {
                "title": "Code Review Session",
                "description": "Weekly code review and knowledge sharing",
                "start_datetime": datetime.utcnow() + timedelta(
                    days=5, hours=15
                ),
                "end_datetime": datetime.utcnow() + timedelta(
                    days=5, hours=16, minutes=30
                ),
                "all_day": False,
                "location": "Development Office",
                "attendees": ["dev-team@company.com"],
                "original_timezone": "UTC",
            },
            {
                "title": "Weekend Hackathon",
                "description": "Innovation hackathon event",
                "start_datetime": datetime.utcnow() + timedelta(days=6),
                "end_datetime": datetime.utcnow() + timedelta(
                    days=8, hours=23, minutes=59, seconds=59
                ),
                "all_day": True,
                "location": "Innovation Lab",
                "attendees": ["all@company.com"],
                "original_timezone": "UTC",
            },
            {
                "title": "Project Kickoff",
                "description": "New project kickoff meeting",
                "start_datetime": datetime.utcnow() + timedelta(
                    days=7, hours=10
                ),
                "end_datetime": datetime.utcnow() + timedelta(
                    days=7, hours=12
                ),
                "all_day": False,
                "location": "Project Room",
                "attendees": ["project-team@company.com"],
                "original_timezone": "UTC",
            },
            {
                "title": "Workshop: AI in Calendar Apps",
                "description": "Technical workshop on implementing AI features",
                "start_datetime": datetime.utcnow() + timedelta(
                    days=10, hours=13
                ),
                "end_datetime": datetime.utcnow() + timedelta(
                    days=10, hours=17
                ),
                "all_day": False,
                "location": "Training Center",
                "attendees": [
                    "engineering@company.com",
                    "ai-team@company.com"
                ],
                "original_timezone": "UTC",
            },
            {
                "title": "Conference: TechCrunch Disrupt",
                "description": "Attending TechCrunch Disrupt conference",
                "start_datetime": datetime.utcnow() + timedelta(days=14),
                "end_datetime": datetime.utcnow() + timedelta(
                    days=16, hours=23, minutes=59, seconds=59
                ),
                "all_day": True,
                "location": "San Francisco, CA",
                "attendees": [],
                "original_timezone": "UTC",
            },
            {
                "title": "Team Building Activity",
                "description": "Quarterly team building event",
                "start_datetime": datetime.utcnow() + timedelta(
                    days=21, hours=14
                ),
                "end_datetime": datetime.utcnow() + timedelta(
                    days=21, hours=18
                ),
                "all_day": False,
                "location": "Adventure Park",
                "attendees": ["team@company.com"],
                "original_timezone": "UTC",
            },
        ]

        # Create events
        events_created = 0
        for event_data in sample_events:
            event = Event(**event_data)
            session.add(event)
            events_created += 1

        await session.commit()
        print(f"✅ Successfully created {events_created} sample events")

        # Print summary
        print("\n📅 Sample Events Created:")
        for event_data in sample_events:
            event_type = "All-day" if event_data["all_day"] else "Timed"
            print(f"  • {event_data['title']} ({event_type})")

        print("\n🎉 Database seeded successfully!")
        print(
            f"You can now run the application and see {events_created} "
            f"sample events."
        )


async def clear_data() -> None:
    """Clear all existing data from the database."""
    print("Clearing existing data...")
    async with async_session_maker() as session:
        # Delete all events
        result = await session.execute("DELETE FROM events")
        deleted_count = result.rowcount
        await session.commit()
        print(f"✅ Deleted {deleted_count} existing events")


if __name__ == "__main__":
    import sys

    async def main():
        if len(sys.argv) > 1 and sys.argv[1] == "--clear":
            await clear_data()
            return

        if len(sys.argv) > 1 and sys.argv[1] == "--reset":
            await clear_data()
            await seed_data()
            return

        await seed_data()

    asyncio.run(main())
