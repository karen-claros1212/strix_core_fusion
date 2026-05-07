from .brain_service import BrainService
from .llm_config import LLMConfig, load_llm_config
from .response_parser import ResponseParser


class LLMRouter:
    def __init__(self, config: LLMConfig | None = None, brain_service: BrainService | None = None):
        self.config = config or load_llm_config()
        self.brain_service = brain_service or BrainService(self.config)
        self.parser = ResponseParser()

    def build_mission_from_natural_language(self, text, context=None) -> dict:
        if not self.config.enabled:
            return self.parser.fallback_mission(text)
        try:
            return self.brain_service.build_mission_from_natural_language(text, context=context)
        except Exception as exc:
            fallback = self.parser.fallback_mission(text)
            fallback["llm_error"] = type(exc).__name__
            return fallback
