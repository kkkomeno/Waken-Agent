"""Model router — selects the appropriate model based on task complexity."""

from enum import Enum

from app.config import settings
from app.core.llm.base import BaseLLM
from app.core.llm.openai_llm import OpenAILLM


class TaskComplexity(str, Enum):
    """Estimated complexity of a user task."""

    SIMPLE = "simple"      # Quick lookup, simple Q&A
    STANDARD = "standard"  # Normal task with tool use
    COMPLEX = "complex"    # Multi-step reasoning, heavy analysis


# Complexity keywords for auto-detection
_COMPLEXITY_HINTS = {
    TaskComplexity.SIMPLE: [
        "翻译", "总结", "什么是", "定义", "简单", "查一下",
        "translate", "summarize", "define", "what is", "lookup",
    ],
    TaskComplexity.COMPLEX: [
        "研究", "分析", "比较", "对比", "设计", "架构", "审查",
        "research", "analyze", "compare", "design", "architecture", "review",
        "multi-step", "综合", "深入", "详细",
    ],
}


class ModelRouter:
    """Routes tasks to the appropriate LLM based on complexity."""

    def __init__(self):
        # Pre-instantiate commonly used models
        self._models: dict[str, BaseLLM] = {}

    def get_model(self, model_name: str | None = None) -> BaseLLM:
        """Get or create a model instance."""
        key = model_name or settings.default_model_name
        if key not in self._models:
            self._models[key] = OpenAILLM(model_name=key)
        return self._models[key]

    def classify_complexity(self, task_description: str) -> TaskComplexity:
        """Heuristic-based task complexity classification."""
        text_lower = task_description.lower()

        # Check for complex indicators first
        for keyword in _COMPLEXITY_HINTS[TaskComplexity.COMPLEX]:
            if keyword in text_lower:
                return TaskComplexity.COMPLEX

        # Check for simple indicators
        for keyword in _COMPLEXITY_HINTS[TaskComplexity.SIMPLE]:
            if keyword in text_lower:
                return TaskComplexity.SIMPLE

        # Default to standard
        return TaskComplexity.STANDARD

    def route(self, task_description: str) -> BaseLLM:
        """Select the best model for the given task."""
        complexity = self.classify_complexity(task_description)

        if complexity == TaskComplexity.SIMPLE:
            model_name = settings.default_model_name  # gpt-4o-mini (cheap)
        elif complexity == TaskComplexity.COMPLEX:
            model_name = settings.complex_model_name  # gpt-4o (premium)
        else:
            model_name = settings.default_model_name

        return self.get_model(model_name)


# Singleton instance
model_router = ModelRouter()
