import json
import re

from .action_normalizer import canonicalize_mission


class ResponseParser:
    def parse_mission(self, content: str, fallback_text: str = "") -> dict:
        data = self._extract_json(content)
        if not isinstance(data, dict):
            return self.fallback_mission(fallback_text or content)
        raw_action = str(data.get("action_type") or data.get("action") or "status").strip() or "status"
        target = str(data.get("target") or "").strip()
        arguments = str(data.get("arguments") or target).strip()
        mission = canonicalize_mission(raw_action, target, arguments, fallback_text)
        mission.update({
            "summary": str(data.get("summary") or "").strip(),
            "source": "llm",
        })
        return mission

    def fallback_mission(self, text: str) -> dict:
        normalized = (text or "").strip()
        if not normalized:
            normalized = "status"
        mission = canonicalize_mission(raw_text=normalized)
        mission.update({
            "summary": "deterministic_fallback",
            "source": "fallback",
        })
        return mission

    def _extract_json(self, content: str):
        if not content:
            return None
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", content, re.DOTALL)
            if not match:
                return None
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                return None
