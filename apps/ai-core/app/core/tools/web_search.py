"""Tavily web search tool."""

from typing import Any

from app.config import settings
from app.core.tools.registry import BaseTool


class WebSearchTool(BaseTool):
    """Search the web using Tavily API and return formatted results."""

    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return (
            "Search the web for current information. "
            "Use this when you need to find facts, news, or information "
            "that may not be in your training data. "
            "Returns title, URL, and content for each result."
        )

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to execute",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results (default: 5, max: 10)",
                    "default": 5,
                },
            },
            "required": ["query"],
        }

    async def execute(self, query: str, max_results: int = 5, **kwargs: Any) -> str:
        """Execute a web search and return formatted results."""
        try:
            from tavily import TavilyClient

            client = TavilyClient(api_key=settings.tavily_api_key)
            response = client.search(query=query, max_results=min(max_results, 10))

            if not response.get("results"):
                return f"No results found for: {query}"

            lines = [f"Search results for '{query}':\n"]
            for i, result in enumerate(response["results"], 1):
                title = result.get("title", "No title")
                url = result.get("url", "")
                content = result.get("content", "No content")
                lines.append(f"{i}. **{title}**\n   URL: {url}\n   {content}\n")

            return "\n".join(lines)

        except ImportError:
            return "Error: tavily-python package is not installed."
        except Exception as e:
            return f"Search error: {str(e)}"
