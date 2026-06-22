"""Pydantic request/response models for the AI Core API."""

from pydantic import BaseModel, Field


class AgentRunRequest(BaseModel):
    """Request to run an Agent on a task."""

    task: str = Field(..., description="The task description", min_length=1)
    system_prompt: str | None = Field(
        None,
        description="Custom system prompt. If omitted, a default is used.",
    )
    model_name: str | None = Field(
        None,
        description="Specific model to use. If omitted, auto-routed.",
    )


class AgentStepResponse(BaseModel):
    """A single step in the Agent's execution trace."""

    step_number: int
    thought: str = ""
    action: str | None = None
    action_input: dict | None = None
    observation: str = ""


class AgentRunResponse(BaseModel):
    """Response from an Agent task execution."""

    success: bool
    answer: str = ""
    steps: list[AgentStepResponse] = []
    total_tokens: int = 0
    total_time_seconds: float = 0.0
    error: str | None = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "ok"
    version: str = "0.0.1"
