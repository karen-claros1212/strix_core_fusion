import json
import re


class ResponseParser:
    def parse_mission(self, content: str, fallback_text: str = "") -> dict:
        data = self._extract_json(content)
        if not isinstance(data, dict):
            return self.fallback_mission(fallback_text or content)
        action_type = str(data.get("action_type") or data.get("action") or "status").strip() or "status"
        target = str(data.get("target") or "").strip()
        arguments = str(data.get("arguments") or target).strip()
        return {
            "action_type": action_type,
            "target": target,
            "arguments": arguments,
            "summary": str(data.get("summary") or "").strip(),
            "source": "llm",
        }

    def fallback_mission(self, text: str) -> dict:
        normalized = (text or "").strip()
        if not normalized:
            normalized = "status"
        parts = normalized.split(maxsplit=1)
        action_type = parts[0]
        target = parts[1] if len(parts) > 1 else ""
        return {
            "action_type": action_type,
            "target": target,
            "arguments": target,
            "summary": "deterministic_fallback",
            "source": "fallback",
        }

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
