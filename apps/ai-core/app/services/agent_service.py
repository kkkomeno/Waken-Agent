"""Agent execution service — orchestrates Agent runs."""

from app.core.agent.loop import ReActAgent
from app.core.llm.router import ModelRouter, model_router
from app.core.tools import register_all_tools
from app.models.schemas import AgentRunResponse, AgentStepResponse

# Ensure tools are registered at startup
tools = register_all_tools()

# Default system prompt template
DEFAULT_SYSTEM_PROMPT = """\
You are Waken-Agent, a helpful AI assistant with the ability to use tools.

You have access to these tools:
- **web_search**: Search the web for current information
- **code_exec**: Execute Python code for calculations and data processing
- **file_read**: Read files from the sandbox
- **file_write**: Write content to files

When given a task:
1. Think about what information you need
2. Use tools to gather information or perform actions
3. Synthesize results into a clear, helpful answer
4. Provide your final answer in Chinese (unless the user asks otherwise)

Always respond in Chinese (Simplified) by default."""


async def run_agent(
    task: str,
    system_prompt: str | None = None,
    model_name: str | None = None,
) -> AgentRunResponse:
    """Run an Agent on a task and return the result."""
    # Select model
    llm = model_router.get_model(model_name) if model_name else model_router.route(task)

    # Create Agent
    agent = ReActAgent(
        system_prompt=system_prompt or DEFAULT_SYSTEM_PROMPT,
        tools=tools,
        llm=llm,
    )

    # Execute
    result = await agent.run(task)

    # Convert to response
    return AgentRunResponse(
        success=result.success,
        answer=result.answer,
        steps=[
            AgentStepResponse(
                step_number=s.step_number,
                thought=s.thought,
                action=s.action,
                action_input=s.action_input,
                observation=s.observation,
            )
            for s in result.steps
        ],
        total_tokens=result.total_tokens,
        total_time_seconds=round(result.total_time, 2),
        error=result.error,
    )
