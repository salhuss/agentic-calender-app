"""AI service for natural language event draft generation."""

import re
from datetime import datetime, timedelta
from typing import Any

from app.models.event import EventDraft


class AIService:
    """Service for AI-powered event draft generation."""

    @staticmethod
    async def generate_event_draft(prompt: str) -> EventDraft:
        """Generate an event draft from natural language prompt.

        This is a rule-based implementation for Phase 1.
        In Phase 2, this would be replaced with a proper ML model.
        """
        extracted_entities = AIService._extract_entities(prompt)

        # Extract basic information
        title = AIService._extract_title(prompt, extracted_entities)
        description = AIService._extract_description(prompt)
        location = AIService._extract_location(prompt)
        attendees = AIService._extract_attendees(prompt)

        # Extract temporal information
        start_datetime, end_datetime, all_day = AIService._extract_datetime_info(
            prompt, extracted_entities
        )

        # Calculate confidence based on how much we extracted
        confidence = AIService._calculate_confidence(
            title, start_datetime, end_datetime, location, attendees
        )

        return EventDraft(
            title=title,
            description=description,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            all_day=all_day,
            location=location,
            attendees=attendees,
            confidence=confidence,
            extracted_entities=extracted_entities,
        )

    @staticmethod
    def _extract_entities(prompt: str) -> dict[str, Any]:
        """Extract entities from the prompt."""
        entities: dict[str, Any] = {
            "times": [],
            "dates": [],
            "locations": [],
            "people": [],
            "keywords": [],
        }

        # Time patterns
        time_patterns = [
            r"\b(\d{1,2}):(\d{2})\s*(am|pm)?\b",  # 3:30 pm
            r"\b(\d{1,2})\s*(am|pm)\b",  # 3 pm
            r"\b(\d{1,2})-(\d{1,2})\s*(am|pm)\b",  # 3-4 pm
            r"\b(\d{1,2}):(\d{2})-(\d{1,2}):(\d{2})\s*(am|pm)?\b",  # 3:30-4:30 pm
        ]

        for pattern in time_patterns:
            matches = re.findall(pattern, prompt, re.IGNORECASE)
            entities["times"].extend(matches)

        # Date patterns
        date_patterns = [
            r"\btomorrow\b",
            r"\btoday\b",
            r"\bnext\s+week\b",
            r"\bnext\s+\w+day\b",  # next monday, tuesday, etc
            r"\b\w+day\b",  # monday, tuesday, etc
            r"\b(\d{1,2})/(\d{1,2})\b",  # 12/25
            r"\b(\w+)\s+(\d{1,2})\b",  # December 25
        ]

        for pattern in date_patterns:
            matches = re.findall(pattern, prompt, re.IGNORECASE)
            if isinstance(matches[0], tuple) if matches else False:
                entities["dates"].extend(matches)
            else:
                entities["dates"].extend(matches)

        # Location patterns (words after 'at', 'in', common venue types)
        location_patterns = [
            r"\bat\s+([A-Za-z\s]+?)(?:\s+with|\s+on|\s+from|$)",
            r"\bin\s+([A-Za-z\s]+?)(?:\s+with|\s+on|\s+from|$)",
            r"\b(cafe|restaurant|office|home|park|gym|library|school|university)\b",
        ]

        for pattern in location_patterns:
            matches = re.findall(pattern, prompt, re.IGNORECASE)
            entities["locations"].extend([match.strip() for match in matches])

        # People patterns (words after 'with')
        people_pattern = r"\bwith\s+([A-Za-z\s,]+?)(?:\s+at|\s+in|\s+on|\s+from|$)"
        matches = re.findall(people_pattern, prompt, re.IGNORECASE)
        for match in matches:
            people = [person.strip() for person in match.split(",")]
            entities["people"].extend(people)

        # Keywords for event type
        event_keywords = [
            "meeting",
            "call",
            "lunch",
            "dinner",
            "appointment",
            "interview",
            "workout",
            "gym",
            "class",
            "lesson",
            "conference",
            "presentation",
        ]

        for keyword in event_keywords:
            if keyword.lower() in prompt.lower():
                entities["keywords"].append(keyword)

        return entities

    @staticmethod
    def _extract_title(prompt: str, entities: dict[str, Any]) -> str:
        """Extract or generate a title from the prompt."""
        # Look for common title patterns
        title_patterns = [
            r"^(.+?)\s+(?:at|on|from|tomorrow|today)",  # Everything before time/date
            r"schedule\s+(.+?)(?:\s+for|\s+at|\s+on|$)",
            r"book\s+(.+?)(?:\s+for|\s+at|\s+on|$)",
        ]

        for pattern in title_patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                if len(title) > 3:  # Minimum reasonable title length
                    return title.title()

        # Fallback: use keywords or first few words
        if entities["keywords"]:
            keyword = entities["keywords"][0].title()
            if entities["people"]:
                return f"{keyword} with {entities['people'][0]}"
            return str(keyword)

        # Last resort: first 5 words
        words = prompt.split()[:5]
        return " ".join(words).title()

    @staticmethod
    def _extract_description(prompt: str) -> str | None:
        """Extract description from prompt."""
        # For now, just return the original prompt as description
        # In a real AI implementation, this would be more sophisticated
        return prompt if len(prompt) > 50 else None

    @staticmethod
    def _extract_location(prompt: str) -> str | None:
        """Extract location from prompt."""
        location_patterns = [
            r"\bat\s+([^,\n]+?)(?:\s+with|\s+on|\s+from|$)",
            r"\bin\s+([^,\n]+?)(?:\s+with|\s+on|\s+from|$)",
        ]

        for pattern in location_patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                # Clean up common false positives
                if len(location) > 2 and not re.match(r"\d", location):
                    return location

        return None

    @staticmethod
    def _extract_attendees(prompt: str) -> list[str]:
        """Extract attendees (email addresses) from prompt."""
        # Email pattern
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        emails = re.findall(email_pattern, prompt)

        return emails

    @staticmethod
    def _extract_datetime_info(
        prompt: str, entities: dict[str, Any]
    ) -> tuple[datetime | None, datetime | None, bool]:
        """Extract start/end datetime and all_day flag."""
        now = datetime.now()
        start_datetime = None
        end_datetime = None
        all_day = False

        # Check for "all day" indicators
        if re.search(r"\ball\s+day\b", prompt, re.IGNORECASE):
            all_day = True

        # Extract date
        base_date = now.date()
        if "tomorrow" in prompt.lower():
            base_date = (now + timedelta(days=1)).date()
        elif re.search(r"\bnext\s+week\b", prompt.lower()):
            base_date = (now + timedelta(weeks=1)).date()
        elif re.search(r"\bmonday\b", prompt.lower()):
            days_ahead = 0 - now.weekday()  # Monday is 0
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            base_date = (now + timedelta(days=days_ahead)).date()
        # Add more day patterns as needed

        # Extract time if not all-day
        if not all_day and entities["times"]:
            time_match = entities["times"][0]
            if len(time_match) >= 2:
                try:
                    hour = int(time_match[0])
                    minute = int(time_match[1]) if time_match[1] else 0

                    # Handle AM/PM
                    if len(time_match) > 2 and time_match[2]:
                        if time_match[2].lower() == "pm" and hour != 12:
                            hour += 12
                        elif time_match[2].lower() == "am" and hour == 12:
                            hour = 0

                    start_datetime = datetime.combine(
                        base_date, datetime.min.time().replace(hour=hour, minute=minute)
                    )

                    # Default 1-hour duration
                    end_datetime = start_datetime + timedelta(hours=1)

                    # Look for duration or end time in prompt
                    duration_match = re.search(
                        r"(\d+)\s*(?:hour|hr)", prompt, re.IGNORECASE
                    )
                    if duration_match:
                        duration_hours = int(duration_match.group(1))
                        end_datetime = start_datetime + timedelta(hours=duration_hours)

                except (ValueError, IndexError):
                    pass

        # If all-day or no specific time, set all-day event
        if all_day or start_datetime is None:
            all_day = True
            start_datetime = datetime.combine(base_date, datetime.min.time())
            end_datetime = datetime.combine(
                base_date, datetime.max.time().replace(microsecond=0)
            )

        return start_datetime, end_datetime, all_day

    @staticmethod
    def _calculate_confidence(
        title: str,
        start_datetime: datetime | None,
        end_datetime: datetime | None,
        location: str | None,
        attendees: list[str],
    ) -> float:
        """Calculate confidence score based on extracted information."""
        score = 0.0
        max_score = 5.0

        # Title (required)
        if title and len(title.strip()) > 3:
            score += 1.0

        # DateTime
        if start_datetime and end_datetime:
            score += 2.0
        elif start_datetime or end_datetime:
            score += 1.0

        # Location
        if location:
            score += 1.0

        # Attendees
        if attendees:
            score += 1.0

        return min(score / max_score, 1.0)
