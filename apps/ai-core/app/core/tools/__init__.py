"""Tool system — register all built-in tools."""

from app.core.tools.code_exec import CodeExecTool
from app.core.tools.file_io import FileReadTool, FileWriteTool
from app.core.tools.registry import BaseTool, ToolRegistry, tool_registry
from app.core.tools.web_search import WebSearchTool


def register_all_tools() -> ToolRegistry:
    """Register all built-in tools and return the registry."""
    tools: list[BaseTool] = [
        WebSearchTool(),
        CodeExecTool(),
        FileReadTool(),
        FileWriteTool(),
    ]
    for tool in tools:
        if tool.name not in tool_registry:
            tool_registry.register(tool)
    return tool_registry


__all__ = [
    "BaseTool",
    "ToolRegistry",
    "tool_registry",
    "register_all_tools",
    "WebSearchTool",
    "CodeExecTool",
    "FileReadTool",
    "FileWriteTool",
]
