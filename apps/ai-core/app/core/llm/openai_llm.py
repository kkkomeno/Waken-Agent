"""OpenAI-compatible LLM implementation (supports OpenAI, DeepSeek, etc.)."""

import json
import re
from typing import AsyncIterator

from openai import AsyncOpenAI

from app.config import settings
from app.core.llm.base import BaseLLM, LLMMessage, LLMResponse


def _parse_dsml_tool_calls(content: str) -> list[dict]:
    """Parse DeepSeek DSML XML format tool calls into OpenAI-compatible format.

    DeepSeek returns tool calls in their custom DSML format:
        <DSML tool_calls>
        <DSML invoke name="tool_name">
        <DSML parameter name="param1" string="true">value</DSML parameter>
        </DSML invoke>
        </DSML tool_calls>

    We need to convert this to OpenAI's JSON format:
        [{"id": "call_1", "type": "function",
          "function": {"name": "tool_name", "arguments": '{"param1":"value"}'}}]
    """
    # Check if content contains DSML tool calls
    if "<DSML" not in content:
        return []

    tool_calls = []
    # Find all invoke blocks
    invoke_pattern = r"<DSML\s+invoke\s+name=\"(\w+)\">(.*?)</DSML\s+invoke>"
    matches = re.findall(invoke_pattern, content, re.DOTALL)

    for i, (tool_name, params_block) in enumerate(matches):
        # Parse parameters
        params = {}
        param_pattern = r"<DSML\s+parameter\s+name=\"(\w+)\"[^>]*>(.*?)</DSML\s+parameter>"
        param_matches = re.findall(param_pattern, params_block, re.DOTALL)

        for param_name, param_value in param_matches:
            # Try to parse JSON values
            try:
                params[param_name] = json.loads(param_value.strip())
            except (json.JSONDecodeError, ValueError):
                params[param_name] = param_value.strip()

        tool_calls.append({
            "id": f"call_{i + 1}",
            "type": "function",
            "function": {
                "name": tool_name,
                "arguments": json.dumps(params),
            },
        })

    return tool_calls


class OpenAILLM(BaseLLM):
    """OpenAI-compatible chat completion provider.

    Works with any provider that supports the OpenAI API format:
    - OpenAI (api.openai.com)
    - DeepSeek (api.deepseek.com) — uses DSML for tool calls
    """

    def __init__(
        self,
        model_name: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
    ):
        self._model = model_name or settings.default_model_name
        self._base_url = base_url

        # Auto-detect provider from base_url
        if base_url and "deepseek" in base_url:
            self._provider = "deepseek"
            api_key = api_key or settings.deepseek_api_key
        else:
            self._provider = "openai"
            api_key = api_key or settings.openai_api_key

        self._client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    @property
    def provider_name(self) -> str:
        return self._provider

    @property
    def model_name(self) -> str:
        return self._model

    def _convert_messages(self, messages: list[LLMMessage]) -> list[dict]:
        """Convert our internal message format to OpenAI/DeepSeek format."""
        converted = []
        for msg in messages:
            openai_msg: dict = {"role": msg.role, "content": msg.content}
            if msg.role == "tool":
                openai_msg["type"] = "tool"
                openai_msg["tool_call_id"] = msg.tool_call_id or ""
            elif msg.role == "assistant":
                if msg.tool_calls:
                    openai_msg["type"] = "assistant"
                    # Ensure each tool call has type: function
                    openai_msg["tool_calls"] = [
                        {**tc, "type": "function"} for tc in msg.tool_calls
                    ]
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
        content = choice.message.content or ""

        # Parse tool calls — DeepSeek uses DSML format, OpenAI uses JSON
        tool_calls = []
        if choice.message.tool_calls:
            # Standard OpenAI format
            tool_calls = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
                for tc in choice.message.tool_calls
            ]
        elif "<DSML" in content:
            # DeepSeek DSML format
            tool_calls = _parse_dsml_tool_calls(content)

        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            finish_reason="tool_calls" if tool_calls else (choice.finish_reason or "stop"),
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
        """Rough estimate: ~2 chars per token for Chinese text."""
        return len(text) // 2
