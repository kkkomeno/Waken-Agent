"""Code execution tool using subprocess (MVP version).

⚠️  Security note: This uses subprocess for simplicity in the MVP.
    Production should use e2b sandbox (e2b.dev) for safe isolated execution.
"""

import subprocess
import tempfile
from pathlib import Path
from typing import Any

from app.core.tools.registry import BaseTool


class CodeExecTool(BaseTool):
    """Execute Python code and return the output."""

    @property
    def name(self) -> str:
        return "code_exec"

    @property
    def description(self) -> str:
        return (
            "Execute Python code and return stdout/stderr. "
            "Use this for calculations, data processing, or running code snippets. "
            "⚠️ For security, this runs in a temp directory. "
            "Do NOT execute untrusted code."
        )

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Python code to execute",
                },
                "timeout": {
                    "type": "integer",
                    "description": "Timeout in seconds (default: 30)",
                    "default": 30,
                },
            },
            "required": ["code"],
        }

    async def execute(self, code: str, timeout: int = 30, **kwargs: Any) -> str:
        """Execute Python code in a subprocess."""
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                script_path = Path(tmpdir) / "script.py"
                script_path.write_text(code, encoding="utf-8")

                result = subprocess.run(
                    ["python", str(script_path)],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=tmpdir,
                )

                output_parts = []
                if result.stdout:
                    output_parts.append(f"[stdout]:\n{result.stdout}")
                if result.stderr:
                    output_parts.append(f"[stderr]:\n{result.stderr}")
                if not output_parts:
                    output_parts.append("[No output]")

                return "\n".join(output_parts)

        except subprocess.TimeoutExpired:
            return f"Error: code execution timed out after {timeout}s"
        except Exception as e:
            return f"Execution error: {str(e)}"
