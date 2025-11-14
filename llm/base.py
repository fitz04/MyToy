"""Base LLM interface."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncGenerator
from pydantic import BaseModel


class Message(BaseModel):
    """Chat message model."""
    role: str  # "user", "assistant", "system"
    content: str


class LLMResponse(BaseModel):
    """LLM response model."""
    content: str
    model: str
    usage: Dict[str, int] = {}
    metadata: Dict[str, Any] = {}


class BaseLLM(ABC):
    """Base class for LLM providers."""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    @abstractmethod
    async def generate(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate a response from the LLM."""
        pass

    @abstractmethod
    async def stream_generate(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream generate a response from the LLM."""
        pass

    def format_messages(self, messages: List[Message]) -> Any:
        """Format messages for the specific LLM API."""
        return [{"role": msg.role, "content": msg.content} for msg in messages]
