"""Base LLM provider interface."""
from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def generate(
        self,
        messages: List[Dict[str, str]],
        context: Dict[str, Any] | None = None,
    ) -> str:
        """
        Generate a response from the LLM.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            context: Optional context dictionary with calendar data

        Returns:
            Generated response string
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the LLM service is available."""
        pass
