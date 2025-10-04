"""LLM-powered event extraction service using Ollama."""
import json
import logging
import re
from datetime import datetime

import ollama
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EventExtraction(BaseModel):
    """Structured event data extracted from natural language."""
    title: str
    description: str | None = None
    start_datetime: str | None = None  # ISO format
    end_datetime: str | None = None    # ISO format
    all_day: bool = False
    location: str | None = None
    attendees: list[str] = []
    confidence: float = 0.0
    reasoning: str = ""


class LLMEventExtractor:
    """Extract event details from natural language using Ollama."""

    def __init__(self, model_name: str = "gemma2:2b"):
        """Initialize the extractor with specified model."""
        self.model_name = model_name
        self.client = ollama.Client()

    def _create_extraction_prompt(self, user_input: str) -> str:
        """Create a structured prompt for event extraction."""
        current_time = datetime.now().isoformat()

        return f"""You are an expert AI assistant specialized in extracting structured
calendar event information from natural language text.

Current date/time: {current_time}

Extract event details from this text: "{user_input}"

Please analyze the text and extract:
1. Event title (required - create meaningful title if not explicit)
2. Description (optional - use original text or summary)
3. Start datetime (ISO format with timezone, relative to current time)
4. End datetime (ISO format with timezone, infer reasonable duration if not specified)
5. All-day event flag (true/false)
6. Location (if mentioned)
7. Attendees (extract email addresses or names mentioned with "with")
8. Confidence score (0.0-1.0 based on clarity of the input)
9. Brief reasoning for your extraction

Return ONLY a valid JSON object with this exact structure:
{{
    "title": "string",
    "description": "string or null",
    "start_datetime": "ISO datetime string or null",
    "end_datetime": "ISO datetime string or null",
    "all_day": boolean,
    "location": "string or null",
    "attendees": ["list of strings"],
    "confidence": number between 0.0 and 1.0,
    "reasoning": "brief explanation of extraction logic"
}}

Examples:
- "Meeting tomorrow 3pm" → start: tomorrow 3pm, end: tomorrow 4pm, title: "Meeting"
- "Lunch with John Friday" → title: "Lunch with John", start: next Friday 12pm
- "All day conference next week" → all_day: true, title: "Conference"

Respond with valid JSON only, no other text."""

    def extract_event_data(self, user_input: str) -> EventExtraction:
        """Extract structured event data from natural language input."""
        try:
            logger.info(f"Extracting event data from: '{user_input}'")

            # Create the extraction prompt
            prompt = self._create_extraction_prompt(user_input)

            # Query the LLM
            response = self.client.chat(
                model=self.model_name,
                messages=[
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                options={
                    'temperature': 0.1,  # Low temperature for consistent extraction
                    'top_p': 0.9,
                    'num_predict': 512,  # Limit response length
                }
            )

            # Extract the response content
            response_content = response['message']['content'].strip()
            logger.info(f"LLM response: {response_content}")

            # Try to parse JSON from the response
            json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                extracted_data = json.loads(json_str)
                return EventExtraction(**extracted_data)
            else:
                logger.warning(
                    "No JSON found in LLM response, falling back to rule-based"
                )
                return self._fallback_extraction(user_input)

        except ollama.ResponseError as e:
            logger.error(f"Ollama error: {e}")
            return self._fallback_extraction(user_input)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            return self._fallback_extraction(user_input)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return self._fallback_extraction(user_input)

    def _fallback_extraction(self, user_input: str) -> EventExtraction:
        """Fallback rule-based extraction when LLM is not available."""
        logger.info("Using fallback rule-based extraction")

        title = "New Event"
        if "meeting" in user_input.lower():
            title = "Meeting"
        elif "lunch" in user_input.lower():
            title = "Lunch"
        elif "call" in user_input.lower():
            title = "Call"
        elif "conference" in user_input.lower():
            title = "Conference"

        # Extract people
        with_match = re.search(r'with\s+([\w\s@.]+)', user_input, re.IGNORECASE)
        if with_match:
            person = with_match.group(1).strip()
            title += f" with {person}"

        return EventExtraction(
            title=title,
            description=user_input,
            start_datetime=None,
            end_datetime=None,
            all_day=False,
            location=None,
            attendees=[],
            confidence=0.3,  # Low confidence for rule-based extraction
            reasoning="Fallback rule-based extraction used due to LLM unavailability"
        )

    def check_model_availability(self) -> bool:
        """Check if the specified model is available in Ollama."""
        try:
            models = self.client.list()
            available_models = [model['name'] for model in models['models']]
            return self.model_name in available_models
        except Exception as e:
            logger.error(f"Error checking model availability: {e}")
            return False


# Example usage and testing
if __name__ == "__main__":
    extractor = LLMEventExtractor()

    # Check if model is available
    if extractor.check_model_availability():
        print(f"✅ Model {extractor.model_name} is available")
    else:
        print(f"❌ Model {extractor.model_name} is not available, will use fallback")

    # Test extractions
    test_inputs = [
        "Meeting with John tomorrow at 3pm",
        "Lunch at Cafe Rio Friday 12:30pm with sarah@company.com",
        "All day conference next week",
        "Call with the team in 2 hours",
        "Workshop from 1-5pm at Innovation Lab"
    ]

    for test_input in test_inputs:
        print(f"\n🔍 Input: '{test_input}'")
        result = extractor.extract_event_data(test_input)
        print(f"📅 Title: {result.title}")
        print(f"⏰ Start: {result.start_datetime}")
        print(f"⏰ End: {result.end_datetime}")
        print(f"📍 Location: {result.location}")
        print(f"👥 Attendees: {result.attendees}")
        print(f"🎯 Confidence: {result.confidence}")
        print(f"💭 Reasoning: {result.reasoning}")
