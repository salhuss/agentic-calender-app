"""Local LLM provider using Ollama."""
import httpx
from typing import Dict, Any, List
from .base import BaseLLMProvider


class LocalLLMProvider(BaseLLMProvider):
    """Local LLM provider using Ollama."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama3.2",
    ):
        """
        Initialize the local LLM provider.

        Args:
            base_url: Ollama API base URL
            model: Model name to use (e.g., 'llama3.2', 'mistral')
        """
        self.base_url = base_url
        self.model = model
        self.timeout = 120.0  # 2 minutes for LLM responses

    async def generate(
        self,
        messages: List[Dict[str, str]],
        context: Dict[str, Any] | None = None,
    ) -> str:
        """Generate a response using Ollama."""
        # Build system prompt with context if provided
        system_message = self._build_system_prompt(context)

        # Prepare messages for Ollama
        ollama_messages = [{"role": "system", "content": system_message}] + messages

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": ollama_messages,
                        "stream": False,
                    },
                )
                response.raise_for_status()
                data = response.json()
                return data["message"]["content"]
        except httpx.HTTPError as e:
            raise Exception(f"Ollama API error: {str(e)}")

    async def health_check(self) -> bool:
        """Check if Ollama is running and the model is available."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Check if Ollama is running
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()

                # Check if the model exists
                data = response.json()
                models = [m["name"] for m in data.get("models", [])]

                # Handle model names with tags (e.g., "llama3.2:latest")
                model_base = self.model.split(":")[0]
                return any(
                    m.startswith(model_base) or m.startswith(self.model) for m in models
                )
        except (httpx.HTTPError, Exception):
            return False

    def _build_system_prompt(self, context: Dict[str, Any] | None) -> str:
        """Build the system prompt with calendar context."""
        base_prompt = """You are an AI calendar assistant. You help users manage their schedule,
find free time, plan events, and organize their calendar efficiently.

You can:
- Analyze their calendar and find free time slots
- Help plan events based on their availability
- Suggest optimal times for tasks based on their schedule
- Break down large tasks (like studying for exams or finishing books) into manageable calendar events
- Answer questions about their upcoming schedule

When suggesting calendar actions:
- Be specific with dates and times
- Consider their existing commitments
- Suggest realistic time blocks
- Ask for confirmation before creating events

Be conversational, helpful, and concise."""

        if not context:
            return base_prompt

        # Add calendar context
        events = context.get("events", [])
        if events:
            base_prompt += "\n\nCurrent calendar events:\n"
            for event in events[:10]:  # Limit to prevent context overflow
                start = event.get("start_datetime", "")
                title = event.get("title", "")
                base_prompt += f"- {title} at {start}\n"

        free_times = context.get("free_times", [])
        if free_times:
            base_prompt += "\n\nAvailable free time slots:\n"
            for slot in free_times[:5]:
                base_prompt += f"- {slot}\n"

        return base_prompt
