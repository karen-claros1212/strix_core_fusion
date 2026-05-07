from .llm_config import LLMConfig, load_llm_config, validate_llm_config
from .openai_compatible_client import OpenAICompatibleClient, LLMResponse
from .prompt_builder import PromptBuilder
from .response_parser import ResponseParser


class BrainService:
    def __init__(self, config: LLMConfig | None = None, client: OpenAICompatibleClient | None = None):
        self.config = config or load_llm_config()
        self.client = client or OpenAICompatibleClient(self.config)
        self.prompts = PromptBuilder()
        self.parser = ResponseParser()
        self.executed_tools = False

    def healthcheck(self) -> dict:
        ok, missing = validate_llm_config(self.config)
        return {"ok": ok and self.config.enabled, "enabled": self.config.enabled, "missing": missing, "provider": self.config.provider}

    def analyze_message(self, text, context=None) -> dict:
        if not self.config.enabled:
            return {"ok": False, "fallback": True, "reason": "llm_disabled", "text": text}
        response = self.client.chat_completion(self.prompts.analysis_prompt(text, context))
        if not response.ok:
            return {"ok": False, "fallback": True, "reason": response.error, "text": text}
        return {"ok": True, "content": response.content, "raw": response.raw}

    def build_mission_from_natural_language(self, text, context=None) -> dict:
        if not self.config.enabled:
            return self.parser.fallback_mission(text)
        response: LLMResponse = self.client.chat_completion(self.prompts.mission_prompt(text, context))
        if not response.ok:
            mission = self.parser.fallback_mission(text)
            mission["llm_error"] = response.error
            return mission
        return self.parser.parse_mission(response.content, fallback_text=text)

    def summarize_tool_output(self, text):
        return self.analyze_message(f"Summarize this tool output safely without executing anything:\n{text}")

    def explain_policy_decision(self, decision):
        return self.analyze_message(f"Explain this policy decision briefly and safely:\n{decision}")
