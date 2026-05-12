from .brain_service import BrainService
from .llm_config import LLMConfig, load_llm_config
from .response_parser import ResponseParser
from ..task_planning import TaskPlanner


class LLMRouter:
    def __init__(self, config: LLMConfig | None = None, brain_service: BrainService | None = None):
        self.config = config or load_llm_config()
        self.brain_service = brain_service or BrainService(self.config)
        self.parser = ResponseParser()
        self.task_planner = TaskPlanner()
        self.last_recovery_metadata: dict | None = None

    def build_task_plan_from_natural_language(self, text, context=None) -> dict:
        plan = self.task_planner.plan(text, context=context)
        intent = self.task_planner.build_execution_intent(plan)
        return {"plan": plan.to_dict(), "intent": intent.to_dict(), "executed": False}

    def build_mission_from_natural_language(self, text, context=None) -> dict:
        if not self.config.enabled:
            mission = self.parser.fallback_mission(text)
            mission["executed"] = False
            return mission
        try:
            mission = self.brain_service.build_mission_from_natural_language(text, context=context)
            self.last_recovery_metadata = getattr(self.brain_service, "last_recovery_metadata", None)
            if self.last_recovery_metadata and self.last_recovery_metadata.get("last_error"):
                mission.setdefault("llm_recovery", self.last_recovery_metadata)
            mission.setdefault("executed", False)
            return mission
        except Exception as exc:
            fallback = self.parser.fallback_mission(text)
            fallback["llm_error"] = type(exc).__name__
            fallback["executed"] = False
            self.last_recovery_metadata = {"router_exception": type(exc).__name__}
            fallback["llm_recovery"] = self.last_recovery_metadata
            return fallback
