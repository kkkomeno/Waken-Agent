"""Abstract LLM interface — all providers implement this."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import AsyncIterator


@dataclass
class LLMMessage:
    """A single message in a conversation."""

    role: str  # "system" | "user" | "assistant" | "tool"
    content: str
    tool_call_id: str | None = None
    tool_calls: list[dict] = field(default_factory=list)


@dataclass
class LLMResponse:
    """Response from an LLM call."""

    content: str
    tool_calls: list[dict] = field(default_factory=list)
    finish_reason: str = "stop"  # "stop" | "tool_calls" | "length"
    usage: dict = field(default_factory=dict)  # {"prompt_tokens": N, "completion_tokens": M}


class BaseLLM(ABC):
    """Abstract base for all LLM providers."""

    @abstractmethod
    async def chat(
        self,
        messages: list[LLMMessage],
        tools: list[dict] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        """Send a chat completion request (non-streaming)."""
        ...

    @abstractmethod
    async def chat_stream(
        self,
        messages: list[LLMMessage],
        tools: list[dict] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        """Send a chat completion request (streaming). Yields content chunks."""
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider identifier (e.g., 'openai', 'ollama')."""
        ...

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the current model name."""
        ...

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Estimate token count for the given text."""
        ...
