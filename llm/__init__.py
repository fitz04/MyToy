"""LLM module for managing multiple LLM providers."""
from .base import BaseLLM, Message, LLMResponse
from .claude import ClaudeLLM
from .openai_llm import OpenAILLM
from .manager import LLMManager

# Optional: Groq provider
try:
    from .groq import GroqLLM
except ImportError:
    GroqLLM = None

# Optional: DeepInfra provider
try:
    from .deepinfra import DeepInfraLLM
except ImportError:
    DeepInfraLLM = None

__all__ = [
    "BaseLLM",
    "Message",
    "LLMResponse",
    "ClaudeLLM",
    "OpenAILLM",
    "LLMManager",
]

if GroqLLM is not None:
    __all__.append("GroqLLM")
if DeepInfraLLM is not None:
    __all__.append("DeepInfraLLM")
