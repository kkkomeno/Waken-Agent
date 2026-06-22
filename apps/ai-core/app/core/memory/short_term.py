"""Short-term conversation memory using sliding window + summarization."""

from app.core.llm.base import LLMMessage


class ConversationMemory:
    """Manages the conversation history for a single Agent session.

    Uses a sliding window approach:
    - System prompt is always kept
    - Recent N messages are kept in full
    - Older messages are summarized to save tokens
    """

    def __init__(self, system_prompt: str, max_messages: int = 20):
        self._system: LLMMessage = LLMMessage(role="system", content=system_prompt)
        self._messages: list[LLMMessage] = []
        self._summary: str = ""
        self._max_messages = max_messages

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation."""
        self._messages.append(LLMMessage(role=role, content=content))
        self._maybe_compress()

    def add_tool_result(self, tool_call_id: str, tool_name: str, result: str) -> None:
        """Add a tool call result to the conversation."""
        self._messages.append(
            LLMMessage(
                role="tool",
                content=result,
                tool_call_id=tool_call_id,
            )
        )

    def get_messages(self) -> list[LLMMessage]:
        """Get all messages for the LLM call, including system prompt."""
        msgs = [self._system]

        if self._summary:
            msgs.append(
                LLMMessage(
                    role="system",
                    content=f"[Previous conversation summary]: {self._summary}",
                )
            )

        msgs.extend(self._messages)
        return msgs

    def _maybe_compress(self) -> None:
        """Compress old messages into a summary if over the limit."""
        if len(self._messages) <= self._max_messages:
            return

        # Keep the most recent half
        keep_count = self._max_messages // 2
        old_messages = self._messages[:-keep_count]
        self._messages = self._messages[-keep_count:]

        # Build a rough summary from old messages
        lines = []
        for msg in old_messages:
            if msg.role in ("user", "assistant"):
                label = "用户" if msg.role == "user" else "助手"
                lines.append(f"{label}: {msg.content[:200]}")
        self._summary = "\n".join(lines)

    def clear(self) -> None:
        """Reset conversation (keep system prompt)."""
        self._messages = []
        self._summary = ""
