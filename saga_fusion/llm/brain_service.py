from .llm_config import LLMConfig, load_llm_config, validate_llm_config
from .openai_compatible_client import OpenAICompatibleClient, LLMResponse
from .prompt_builder import PromptBuilder
from .response_parser import ResponseParser
from ..task_planning import TaskPlanner
from ..memory import MemoryStore, MemoryRetriever, ContextWindow


class BrainService:
    def __init__(self, config: LLMConfig | None = None, client: OpenAICompatibleClient | None = None, memory_store: MemoryStore | None = None):
        self.config = config or load_llm_config()
        self.client = client or OpenAICompatibleClient(self.config)
        self.memory_store = memory_store or MemoryStore()
        self.memory_retriever = MemoryRetriever(self.memory_store)
        self.context_window = ContextWindow(char_budget=2000)
        self.prompts = PromptBuilder(self.context_window)
        self.parser = ResponseParser()
        self.task_planner = TaskPlanner()
        self.executed_tools = False

    def healthcheck(self) -> dict:
        ok, missing = validate_llm_config(self.config)
        return {"ok": ok and self.config.enabled, "enabled": self.config.enabled, "missing": missing, "provider": self.config.provider}

    def _merge_memory_context(self, text, context=None, mission_id: str | None = None):
        retrieved = self.memory_retriever.retrieve(str(text or ""), mission_id=mission_id, limit=3).as_context_items()
        if context is None:
            return retrieved
        if isinstance(context, (list, tuple)):
            return tuple(context) + retrieved
        if retrieved:
            return (str(context),) + retrieved
        return context

    def analyze_message(self, text, context=None) -> dict:
        context = self._merge_memory_context(text, context)
        if not self.config.enabled:
            return {"ok": False, "fallback": True, "reason": "llm_disabled", "text": text}
        response = self.client.chat_completion(self.prompts.analysis_prompt(text, context))
        if not response.ok:
            return {"ok": False, "fallback": True, "reason": response.error, "text": text}
        return {"ok": True, "content": response.content, "raw": response.raw}

    def build_mission_from_natural_language(self, text, context=None) -> dict:
        context = self._merge_memory_context(text, context)
        if not self.config.enabled:
            return self.parser.fallback_mission(text)
        response: LLMResponse = self.client.chat_completion(self.prompts.mission_prompt(text, context))
        if not response.ok:
            mission = self.parser.fallback_mission(text)
            mission["llm_error"] = response.error
            return mission
        return self.parser.parse_mission(response.content, fallback_text=text)

    def build_task_plan_from_natural_language(self, text, context=None) -> dict:
        plan = self.task_planner.plan(text, context=context)
        intent = self.task_planner.build_execution_intent(plan)
        return {"plan": plan.to_dict(), "intent": intent.to_dict(), "executed": False}

    def summarize_tool_output(self, text):
        return self.analyze_message(f"Summarize this tool output safely without executing anything:\n{text}")

    def explain_policy_decision(self, decision):
        return self.analyze_message(f"Explain this policy decision briefly and safely:\n{decision}")
