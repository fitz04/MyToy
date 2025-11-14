"""OpenAI LLM implementation."""
from typing import List, Optional, AsyncGenerator
from openai import AsyncOpenAI
from .base import BaseLLM, Message, LLMResponse


class OpenAILLM(BaseLLM):
    """OpenAI LLM implementation."""

    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview"):
        super().__init__(api_key, model)
        self.client = AsyncOpenAI(api_key=api_key)

    async def generate(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: Optional[int] = 4096,
        **kwargs
    ) -> LLMResponse:
        """Generate a response from OpenAI."""
        formatted_messages = self.format_messages(messages)

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

        return LLMResponse(
            content=response.choices[0].message.content,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            metadata={"finish_reason": response.choices[0].finish_reason}
        )

    async def stream_generate(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: Optional[int] = 4096,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream generate a response from OpenAI."""
        formatted_messages = self.format_messages(messages)

        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
