"""
ReAct Agent Loop — the core execution engine.

ReAct = Reasoning + Acting

Cycle:
  1. Think: LLM receives current state → decides next action
  2. Act: Execute the chosen tool (or return final answer)
  3. Observe: Feed tool result back as context
  4. Repeat until: task complete OR max steps OR timeout
"""

import json
import time
from typing import AsyncIterator

from app.config import settings
from app.core.llm.base import BaseLLM, LLMMessage, LLMResponse
from app.core.llm.router import ModelRouter, model_router
from app.core.memory.short_term import ConversationMemory
from app.core.tools.registry import ToolRegistry, tool_registry


class AgentStep:
    """Record of a single step in the Agent's execution."""

    def __init__(self, step_number: int):
        self.step_number = step_number
        self.thought: str = ""
        self.action: str | None = None  # tool name or "final_answer"
        self.action_input: dict | None = None
        self.observation: str = ""
        self.timestamp: float = time.time()


class AgentResult:
    """Final result of an Agent execution."""

    def __init__(self):
        self.success: bool = False
        self.answer: str = ""
        self.steps: list[AgentStep] = []
        self.total_tokens: int = 0
        self.total_time: float = 0.0
        self.error: str | None = None


class ReActAgent:
    """A single Agent that can execute tasks using the ReAct pattern.

    Usage:
        agent = ReActAgent(
            system_prompt="You are a helpful research assistant.",
            tools=tool_registry,
            llm=model_router.route("research task"),
        )
        result = await agent.run("Research the latest AI trends")
    """

    def __init__(
        self,
        system_prompt: str,
        tools: ToolRegistry | None = None,
        llm: BaseLLM | None = None,
        max_steps: int | None = None,
        timeout: int | None = None,
    ):
        self.system_prompt = system_prompt
        self.tools = tools or tool_registry
        self.llm = llm or model_router.get_model()
        self.max_steps = max_steps or settings.default_max_steps
        self.timeout = timeout or settings.default_timeout
        self.memory: ConversationMemory | None = None

    async def run(self, task: str) -> AgentResult:
        """Execute a task and return the final result."""
        result = AgentResult()
        start_time = time.time()

        self.memory = ConversationMemory(self.system_prompt)
        self.memory.add_message("user", task)

        try:
            for step_num in range(1, self.max_steps + 1):
                # Check timeout
                if time.time() - start_time > self.timeout:
                    result.error = f"Timeout after {self.timeout}s"
                    break

                step = AgentStep(step_num)

                # 1. THINK: Get LLM response
                llm_response = await self._think(step)
                result.total_tokens += llm_response.usage.get("total_tokens", 0)

                # 2. Check if final answer
                if llm_response.finish_reason == "stop" and not llm_response.tool_calls:
                    result.answer = llm_response.content
                    result.success = True
                    step.thought = llm_response.content
                    step.action = "final_answer"
                    result.steps.append(step)
                    self.memory.add_message("assistant", llm_response.content)
                    break

                # 3. ACT: Execute tool calls
                if llm_response.tool_calls:
                    await self._act(llm_response, step)
                    result.steps.append(step)

                # 4. Continue loop (OBSERVE happens via memory in next iteration)

            else:
                # Max steps reached without final answer
                result.error = f"Max steps ({self.max_steps}) reached"
                # Try to get a final answer
                self.memory.add_message(
                    "user",
                    "Please provide your final answer now based on what you've found.",
                )
                final_response = await self.llm.chat(self.memory.get_messages())
                result.answer = final_response.content
                result.success = True

        except Exception as e:
            result.error = str(e)

        result.total_time = time.time() - start_time
        return result

    async def run_stream(self, task: str) -> AsyncIterator[str]:
        """Execute a task with streaming — yields progress updates."""
        self.memory = ConversationMemory(self.system_prompt)
        self.memory.add_message("user", task)

        yield f"📋 任务: {task}\n\n"

        for step_num in range(1, self.max_steps + 1):
            yield f"--- Step {step_num} ---\n"

            # THINK (stream the LLM's response)
            llm_response = await self._think_stream()

            if llm_response.finish_reason == "stop" and not llm_response.tool_calls:
                yield f"\n✅ 最终答案:\n{llm_response.content}"
                break

            if llm_response.tool_calls:
                for tc in llm_response.tool_calls:
                    tool_name = tc["function"]["name"]
                    yield f"🔧 调用工具: {tool_name}\n"

                    # ACT
                    observation = await self._execute_tool(tc)
                    yield f"📊 结果:\n{observation[:500]}...\n\n"

            yield "\n"

    async def _think(self, step: AgentStep) -> LLMResponse:
        """Get the LLM's next action."""
        messages = self.memory.get_messages() if self.memory else []
        tools_schema = self.tools.get_openai_schemas() if self.tools else None
        response = await self.llm.chat(messages, tools=tools_schema)
        step.thought = response.content
        return response

    async def _think_stream(self) -> LLMResponse:
        """Get LLM response (non-streaming for now — streaming tool calls is complex)."""
        messages = self.memory.get_messages() if self.memory else []
        tools_schema = self.tools.get_openai_schemas() if self.tools else None
        return await self.llm.chat(messages, tools=tools_schema)

    async def _act(self, llm_response: LLMResponse, step: AgentStep) -> None:
        """Execute all tool calls from the LLM response."""
        # Add assistant message with tool calls
        assistant_msg = LLMMessage(
            role="assistant",
            content=llm_response.content or "",
            tool_calls=llm_response.tool_calls,
        )
        if self.memory:
            assistant_msg.tool_calls = llm_response.tool_calls
            self.memory._messages.append(assistant_msg)

        for tc in llm_response.tool_calls:
            tool_name = tc["function"]["name"]
            step.action = tool_name

            try:
                args = json.loads(tc["function"]["arguments"])
            except json.JSONDecodeError:
                args = {}

            step.action_input = args

            # Execute the tool
            observation = await self._execute_tool(tc)
            step.observation = observation

    async def _execute_tool(self, tool_call: dict) -> str:
        """Execute a single tool and record the result in memory."""
        tool_name = tool_call["function"]["name"]
        tool = self.tools.get(tool_name)

        if tool is None:
            result = f"Error: unknown tool '{tool_name}'"
        else:
            try:
                args = json.loads(tool_call["function"]["arguments"])
            except json.JSONDecodeError:
                args = {}
            result = await tool.execute(**args)

        # Feed observation back to memory
        if self.memory:
            self.memory.add_tool_result(
                tool_call_id=tool_call.get("id", ""),
                tool_name=tool_name,
                result=result,
            )

        return result
