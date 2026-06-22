"""OpenAI LLM implementation."""

from typing import AsyncIterator

from openai import AsyncOpenAI

from app.config import settings
from app.core.llm.base import BaseLLM, LLMMessage, LLMResponse


class OpenAILLM(BaseLLM):
    """OpenAI chat completion provider."""

    def __init__(self, model_name: str | None = None):
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        self._model = model_name or settings.default_model_name

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def model_name(self) -> str:
        return self._model

    def _convert_messages(self, messages: list[LLMMessage]) -> list[dict]:
        """Convert our internal message format to OpenAI's format."""
        converted = []
        for msg in messages:
            openai_msg: dict = {"role": msg.role, "content": msg.content}
            if msg.tool_call_id:
                openai_msg["tool_call_id"] = msg.tool_call_id
            if msg.tool_calls:
                openai_msg["tool_calls"] = msg.tool_calls
            converted.append(openai_msg)
        return converted

    async def chat(
        self,
        messages: list[LLMMessage],
        tools: list[dict] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        """Non-streaming chat completion."""
        kwargs: dict = {
            "model": self._model,
            "messages": self._convert_messages(messages),
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if tools:
            kwargs["tools"] = tools

        response = await self._client.chat.completions.create(**kwargs)

        choice = response.choices[0]
        return LLMResponse(
            content=choice.message.content or "",
            tool_calls=[
                {
                    "id": tc.id,
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
                for tc in (choice.message.tool_calls or [])
            ],
            finish_reason=choice.finish_reason or "stop",
            usage={
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
            },
        )

    async def chat_stream(
        self,
        messages: list[LLMMessage],
        tools: list[dict] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        """Streaming chat completion — yields content chunks as they arrive."""
        kwargs: dict = {
            "model": self._model,
            "messages": self._convert_messages(messages),
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }
        if tools:
            kwargs["tools"] = tools

        stream = await self._client.chat.completions.create(**kwargs)
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def count_tokens(self, text: str) -> int:
        """Rough estimate: ~4 chars per token for English."""
        return len(text) // 4
