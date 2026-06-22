"""File I/O tool — read and write files in a sandboxed directory."""

from pathlib import Path
from typing import Any

from app.core.tools.registry import BaseTool

# Sandbox directory for file operations
_SANDBOX_DIR = Path("data/sandbox")


class FileReadTool(BaseTool):
    """Read contents of a file."""

    @property
    def name(self) -> str:
        return "file_read"

    @property
    def description(self) -> str:
        return (
            "Read the contents of a file. "
            "Use this to view files that have been previously written or downloaded."
        )

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file (relative to sandbox directory)",
                },
            },
            "required": ["path"],
        }

    async def execute(self, path: str, **kwargs: Any) -> str:
        """Read file contents."""
        try:
            full_path = (_SANDBOX_DIR / path).resolve()
            # Security: ensure we don't escape sandbox
            if not str(full_path).startswith(str(_SANDBOX_DIR.resolve())):
                return "Error: path is outside sandbox directory"

            if not full_path.exists():
                return f"Error: file not found: {path}"

            content = full_path.read_text(encoding="utf-8")
            return f"Contents of {path}:\n\n{content}"

        except Exception as e:
            return f"File read error: {str(e)}"


class FileWriteTool(BaseTool):
    """Write content to a file."""

    @property
    def name(self) -> str:
        return "file_write"

    @property
    def description(self) -> str:
        return (
            "Write content to a file. Creates the file if it doesn't exist. "
            "Use this to save generated code, reports, or data."
        )

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file (relative to sandbox directory)",
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to the file",
                },
            },
            "required": ["path", "content"],
        }

    async def execute(self, path: str, content: str, **kwargs: Any) -> str:
        """Write content to a file."""
        try:
            full_path = (_SANDBOX_DIR / path).resolve()
            # Security: ensure we don't escape sandbox
            if not str(full_path).startswith(str(_SANDBOX_DIR.resolve())):
                return "Error: path is outside sandbox directory"

            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding="utf-8")
            return f"Successfully wrote {len(content)} bytes to {path}"

        except Exception as e:
            return f"File write error: {str(e)}"
