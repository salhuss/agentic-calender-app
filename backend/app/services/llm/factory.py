"""LLM provider factory."""
from app.core.config import settings
from .base import BaseLLMProvider
from .local import LocalLLMProvider


def get_llm_provider() -> BaseLLMProvider:
    """
    Get the configured LLM provider.

    Returns:
        An instance of the configured LLM provider
    """
    provider_type = getattr(settings, "LLM_PROVIDER", "local").lower()

    if provider_type == "local":
        ollama_url = getattr(settings, "OLLAMA_BASE_URL", "http://localhost:11434")
        ollama_model = getattr(settings, "OLLAMA_MODEL", "llama3.2")
        return LocalLLMProvider(base_url=ollama_url, model=ollama_model)
    elif provider_type == "openai":
        # Future: OpenAI provider
        raise NotImplementedError("OpenAI provider not yet implemented")
    elif provider_type == "anthropic":
        # Future: Anthropic provider
        raise NotImplementedError("Anthropic provider not yet implemented")
    else:
        raise ValueError(f"Unknown LLM provider: {provider_type}")
