"""Claude (Anthropic) LLM implementation."""
from typing import List, Optional, AsyncGenerator
from anthropic import AsyncAnthropic
from .base import BaseLLM, Message, LLMResponse


class ClaudeLLM(BaseLLM):
    """Claude LLM implementation using Anthropic API."""

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        super().__init__(api_key, model)
        self.client = AsyncAnthropic(api_key=api_key)

    async def generate(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: Optional[int] = 4096,
        **kwargs
    ) -> LLMResponse:
        """Generate a response from Claude."""
        # Separate system messages
        system_message = None
        chat_messages = []

        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                chat_messages.append({"role": msg.role, "content": msg.content})

        # Call Claude API
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_message if system_message else None,
            messages=chat_messages,
            **kwargs
        )

        return LLMResponse(
            content=response.content[0].text,
            model=response.model,
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
            metadata={"stop_reason": response.stop_reason}
        )

    async def stream_generate(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: Optional[int] = 4096,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream generate a response from Claude."""
        # Separate system messages
        system_message = None
        chat_messages = []

        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                chat_messages.append({"role": msg.role, "content": msg.content})

        # Stream from Claude API
        async with self.client.messages.stream(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_message if system_message else None,
            messages=chat_messages,
            **kwargs
        ) as stream:
            async for text in stream.text_stream:
                yield text
