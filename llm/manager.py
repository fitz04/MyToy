"""LLM Manager for handling multiple LLM providers."""
from typing import Optional, List, AsyncGenerator
from config import settings
from .base import BaseLLM, Message, LLMResponse
from .claude import ClaudeLLM
from .openai_llm import OpenAILLM
from .groq import GroqLLM
from .deepinfra import DeepInfraLLM


class LLMManager:
    """Manager class for handling multiple LLM providers."""

    def __init__(self):
        self.current_provider = settings.default_llm_provider
        self._llm_cache = {}

    def _get_llm(self, provider: str) -> BaseLLM:
        """Get or create LLM instance for the specified provider."""
        if provider in self._llm_cache:
            return self._llm_cache[provider]

        api_key = settings.get_api_key(provider)
        model = settings.get_model_name(provider)

        if not api_key:
            raise ValueError(f"API key not found for provider: {provider}")

        llm_classes = {
            "claude": ClaudeLLM,
            "openai": OpenAILLM,
            "groq": GroqLLM,
            "deepinfra": DeepInfraLLM,
        }

        llm_class = llm_classes.get(provider)
        if not llm_class:
            raise ValueError(f"Unknown LLM provider: {provider}")

        llm = llm_class(api_key=api_key, model=model)
        self._llm_cache[provider] = llm
        return llm

    def switch_provider(self, provider: str) -> str:
        """Switch to a different LLM provider."""
        if provider not in ["claude", "openai", "groq", "deepinfra"]:
            raise ValueError(f"Invalid provider: {provider}")

        self.current_provider = provider
        return f"Switched to {provider}"

    def get_current_provider(self) -> str:
        """Get the current LLM provider."""
        return self.current_provider

    async def generate(
        self,
        messages: List[Message],
        provider: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate a response using the specified or current provider."""
        provider = provider or self.current_provider
        llm = self._get_llm(provider)
        return await llm.generate(messages, temperature, max_tokens, **kwargs)

    async def stream_generate(
        self,
        messages: List[Message],
        provider: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream generate a response using the specified or current provider."""
        provider = provider or self.current_provider
        llm = self._get_llm(provider)
        async for chunk in llm.stream_generate(messages, temperature, max_tokens, **kwargs):
            yield chunk

    def list_providers(self) -> List[str]:
        """List all available LLM providers."""
        return ["claude", "openai", "groq", "deepinfra"]

    def get_provider_info(self, provider: Optional[str] = None) -> dict:
        """Get information about the specified or current provider."""
        provider = provider or self.current_provider
        return {
            "provider": provider,
            "model": settings.get_model_name(provider),
            "has_api_key": bool(settings.get_api_key(provider))
        }
