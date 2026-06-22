"""
Tool Registry — pluggable tool system for AI Agents.

Each tool has:
- name: unique identifier
- description: tells the LLM what the tool does
- parameters: JSON Schema describing the tool's inputs
- execute(): the actual implementation
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):
    """Abstract base for all tools."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique tool identifier."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description — used by the LLM to decide when to call this tool."""
        ...

    @property
    @abstractmethod
    def parameters(self) -> dict:
        """JSON Schema for the tool's input parameters."""
        ...

    @abstractmethod
    async def execute(self, **kwargs: Any) -> str:
        """Execute the tool with the given parameters. Returns result as string."""
        ...

    def to_openai_schema(self) -> dict:
        """Convert to OpenAI function calling format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


class ToolRegistry:
    """Central registry for all available tools."""

    _instance: "ToolRegistry | None" = None

    def __init__(self):
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """Register a tool."""
        self._tools[tool.name] = tool
        print(f"[ToolRegistry] Registered tool: {tool.name}")

    def get(self, name: str) -> BaseTool | None:
        """Get a tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> list[BaseTool]:
        """Get all registered tools."""
        return list(self._tools.values())

    def get_openai_schemas(self) -> list[dict]:
        """Get all tools in OpenAI function-calling format."""
        return [tool.to_openai_schema() for tool in self._tools.values()]

    def __contains__(self, name: str) -> bool:
        return name in self._tools


# Global singleton
tool_registry = ToolRegistry()
