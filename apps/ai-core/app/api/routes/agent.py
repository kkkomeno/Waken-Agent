"""Agent execution API endpoints."""

from fastapi import APIRouter, HTTPException

from app.models.schemas import AgentRunRequest, AgentRunResponse
from app.services.agent_service import run_agent

router = APIRouter(prefix="/api/v1", tags=["agent"])


@router.post("/run", response_model=AgentRunResponse)
async def run_agent_endpoint(request: AgentRunRequest) -> AgentRunResponse:
    """
    Run an AI Agent on a task.

    The Agent will:
    1. Analyze the task
    2. Use available tools (web search, code execution, file I/O)
    3. Return a synthesized answer with execution trace
    """
    try:
        return await run_agent(
            task=request.task,
            system_prompt=request.system_prompt,
            model_name=request.model_name,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")
