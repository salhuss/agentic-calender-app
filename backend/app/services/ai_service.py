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

        # Time patterns - FIXED: Now properly structured
        # IMPORTANT: Check Pattern 2 first (hour:minute) to avoid Pattern 1 matching the minutes

        # Pattern 2: "3:30pm" or "3:30 pm" -> (hour, minute, am_pm)
        pattern2 = r"\b(\d{1,2}):(\d{2})\s*(am|pm)\b"
        for match in re.finditer(pattern2, prompt, re.IGNORECASE):
            entities["times"].append(
                {
                    "type": "single",
                    "hour": match.group(1),
                    "minute": match.group(2),
                    "am_pm": match.group(3),
                    "raw": match.group(0),
                }
            )

        # Pattern 1: "3pm" or "3 pm" -> (hour, am_pm)
        # Collect positions of already-matched times to avoid duplicates
        matched_positions = [
            (prompt.find(t["raw"]), prompt.find(t["raw"]) + len(t["raw"]))
            for t in entities["times"]
        ]

        pattern1 = r"\b(\d{1,2})\s*(am|pm)\b"
        for match in re.finditer(pattern1, prompt, re.IGNORECASE):
            # Skip if this overlaps with an already-captured time
            match_start, match_end = match.start(), match.end()
            overlaps = any(
                (match_start >= start and match_start < end)
                or (match_end > start and match_end <= end)
                for start, end in matched_positions
            )
            if not overlaps:
                entities["times"].append(
                    {
                        "type": "single",
                        "hour": match.group(1),
                        "minute": "0",
                        "am_pm": match.group(2),
                        "raw": match.group(0),
                    }
                )

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

        # People patterns (words after 'with') - FIXED: More precise boundaries
        people_pattern = r"\bwith\s+([A-Za-z\s,]+?)(?:\s+at\s+|\s+in\s+|\s+on\s+|\s+from\s+|\s+tomorrow\b|\s+today\b|\s+next\s+|\s+\d{1,2}(?:am|pm|:)|$)"
        matches = re.findall(people_pattern, prompt, re.IGNORECASE)
        for match in matches:
            # Clean up and split by commas
            people = [person.strip() for person in match.split(",") if person.strip()]
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
        """Extract location from prompt - FIXED: Better boundaries."""
        # Pattern: "at <location>" but stop before time/date indicators
        location_patterns = [
            r"\bat\s+([A-Za-z][A-Za-z0-9\s]+?)(?:\s+(?:with|on|from|tomorrow|today|next|monday|tuesday|wednesday|thursday|friday|saturday|sunday|\d{1,2}(?:am|pm|:))|\s*$)",
            r"\bin\s+([A-Za-z][A-Za-z0-9\s]+?)(?:\s+(?:with|on|from|tomorrow|today|next|monday|tuesday|wednesday|thursday|friday|saturday|sunday|\d{1,2}(?:am|pm|:))|\s*$)",
        ]

        for pattern in location_patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                # Clean up: remove trailing punctuation and common false positives
                location = re.sub(r"[,.\s]+$", "", location)

                # Validate it's a reasonable location (not just a time or number)
                if len(location) > 2 and not re.match(r"^[\d\s:]+$", location):
                    # Don't return if it's just a single word that looks like a day
                    days = [
                        "monday",
                        "tuesday",
                        "wednesday",
                        "thursday",
                        "friday",
                        "saturday",
                        "sunday",
                    ]
                    if location.lower() not in days:
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

        # Extract date - IMPROVED: Better day-of-week handling
        base_date = now.date()
        prompt_lower = prompt.lower()

        if "tomorrow" in prompt_lower:
            base_date = (now + timedelta(days=1)).date()
        elif "today" in prompt_lower:
            base_date = now.date()
        elif re.search(r"\bnext\s+week\b", prompt_lower):
            base_date = (now + timedelta(weeks=1)).date()
        else:
            # Check for specific days of week
            days_map = {
                "monday": 0,
                "tuesday": 1,
                "wednesday": 2,
                "thursday": 3,
                "friday": 4,
                "saturday": 5,
                "sunday": 6,
            }
            for day_name, day_num in days_map.items():
                if day_name in prompt_lower:
                    days_ahead = day_num - now.weekday()
                    if days_ahead <= 0:  # Target day already happened this week
                        days_ahead += 7
                    base_date = (now + timedelta(days=days_ahead)).date()
                    break

        # Extract time if not all-day - FIXED: Use new dict structure
        if not all_day and entities["times"]:
            time_info = entities["times"][0]  # Get first time mentioned
            try:
                hour = int(time_info["hour"])
                minute = int(time_info["minute"])
                am_pm = time_info["am_pm"].lower()

                # Handle AM/PM conversion
                if am_pm == "pm" and hour != 12:
                    hour += 12
                elif am_pm == "am" and hour == 12:
                    hour = 0

                start_datetime = datetime.combine(
                    base_date, datetime.min.time().replace(hour=hour, minute=minute)
                )

                # Default 1-hour duration
                end_datetime = start_datetime + timedelta(hours=1)

                # Look for duration or end time in prompt
                duration_match = re.search(
                    r"(\d+)\s*(?:hour|hr)s?\b", prompt, re.IGNORECASE
                )
                if duration_match:
                    duration_hours = int(duration_match.group(1))
                    end_datetime = start_datetime + timedelta(hours=duration_hours)

            except (ValueError, KeyError, IndexError) as e:
                # If time parsing fails, fall back to all-day
                all_day = True

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
