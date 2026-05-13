from __future__ import annotations

import re

from .detection_rule_types import DetectionRule, RuleFormat, validate_defensive_request


class YaraRuleBuilder:
    """Build metadata/string-only defensive YARA templates."""

    def build_rule(self, name: str, strings: list[str] | tuple[str, ...], *, description: str = "Defensive malware triage rule", tags: tuple[str, ...] = ("defensive",), author: str = "STRIX defensive knowledge") -> DetectionRule:
        validate_defensive_request(name, description, strings, tags)
        rule_name = self._safe_name(name)
        safe_strings = [self._safe_string(s) for s in strings or [] if str(s or "").strip()]
        if not rule_name:
            raise ValueError("YARA rule name is required")
        if not safe_strings:
            raise ValueError("At least one defensive detection string is required")
        lines = [f"rule {rule_name} : {' '.join(self._safe_tag(t) for t in tags if t) or 'defensive'} {{", "  meta:"]
        lines.extend([
            f"    description = \"{self._escape(description)}\"",
            f"    author = \"{self._escape(author)}\"",
            "    defensive_only = true",
            "    execution_allowed = false",
            "    non_authoritative = true",
        ])
        lines.append("  strings:")
        for idx, value in enumerate(safe_strings, start=1):
            lines.append(f"    $s{idx} = \"{self._escape(value)}\" ascii wide nocase")
        lines.extend(["  condition:", "    any of them", "}"])
        return DetectionRule(rule_name, RuleFormat.YARA, "\n".join(lines), description, tuple(tags), "medium", False, {"defensive_only": True, "string_count": len(safe_strings)})

    @staticmethod
    def _safe_name(name: str) -> str:
        cleaned = re.sub(r"[^A-Za-z0-9_]", "_", str(name or "").strip())
        if cleaned and cleaned[0].isdigit():
            cleaned = "rule_" + cleaned
        return cleaned[:80]

    @staticmethod
    def _safe_tag(tag: str) -> str:
        return re.sub(r"[^A-Za-z0-9_]", "_", str(tag or "defensive").strip())[:40] or "defensive"

    @staticmethod
    def _safe_string(value: str) -> str:
        text = str(value or "").replace("\x00", "").strip()
        if len(text) > 160:
            raise ValueError("Detection strings must be short metadata indicators, not payloads")
        validate_defensive_request(text)
        return text

    @staticmethod
    def _escape(value: str) -> str:
        return str(value).replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")
