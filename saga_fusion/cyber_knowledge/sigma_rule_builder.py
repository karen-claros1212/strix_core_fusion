from __future__ import annotations

import re
import uuid

from .detection_rule_types import DetectionRule, RuleFormat, validate_defensive_request


class SigmaRuleBuilder:
    """Build defensive Sigma YAML templates for log correlation."""

    def build_rule(self, title: str, logsource: dict, detection: dict, *, description: str = "Defensive log detection rule", level: str = "medium", tags: tuple[str, ...] = ("attack.defense_evasion",)) -> DetectionRule:
        validate_defensive_request(title, description, logsource, detection, tags)
        if not str(title or "").strip():
            raise ValueError("Sigma title is required")
        if not isinstance(logsource, dict) or not logsource:
            raise ValueError("Sigma logsource metadata is required")
        if not isinstance(detection, dict) or not detection:
            raise ValueError("Sigma detection metadata is required")
        safe_title = self._scalar(title)
        safe_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, safe_title + repr(logsource) + repr(detection)))
        lines = [
            f"title: {safe_title}",
            f"id: {safe_id}",
            "status: experimental",
            f"description: {self._scalar(description)}",
            "references:",
            "  - internal:defensive-triage-template",
            "author: STRIX defensive knowledge",
            "date: 2026/05/13",
            "tags:",
        ]
        for tag in tags or ("defensive",):
            lines.append(f"  - {self._scalar(tag)}")
        lines.append("logsource:")
        self._append_mapping(lines, logsource, indent=2)
        lines.append("detection:")
        self._append_mapping(lines, detection, indent=2)
        if "condition" not in {str(k).lower() for k in detection.keys()}:
            lines.append("  condition: selection")
        lines.extend([
            f"level: {self._level(level)}",
            "fields:",
            "  - Image",
            "  - CommandLine",
            "  - User",
            "falsepositives:",
            "  - Legitimate administrative or security tooling; validate before action.",
            "x_strix_safety:",
            "  defensive_only: true",
            "  execution_allowed: false",
            "  non_authoritative: true",
        ])
        name = re.sub(r"[^A-Za-z0-9_]+", "_", str(title).strip().lower()).strip("_")[:80] or "sigma_defensive_rule"
        return DetectionRule(name, RuleFormat.SIGMA, "\n".join(lines), description, tuple(tags), self._level(level), False, {"defensive_only": True})

    def _append_mapping(self, lines: list[str], mapping: dict, indent: int) -> None:
        pad = " " * indent
        for key, value in mapping.items():
            key_text = re.sub(r"[^A-Za-z0-9_|.-]", "_", str(key))
            if isinstance(value, dict):
                lines.append(f"{pad}{key_text}:")
                self._append_mapping(lines, value, indent + 2)
            elif isinstance(value, (list, tuple)):
                lines.append(f"{pad}{key_text}:")
                for item in value:
                    validate_defensive_request(item)
                    lines.append(f"{pad}  - {self._scalar(item)}")
            else:
                validate_defensive_request(value)
                lines.append(f"{pad}{key_text}: {self._scalar(value)}")

    @staticmethod
    def _scalar(value: object) -> str:
        text = str(value or "").replace("\x00", "").replace("\n", " ").strip()
        if len(text) > 220:
            raise ValueError("Sigma scalar values must be concise metadata, not payloads")
        validate_defensive_request(text)
        if text == "":
            return "''"
        if re.search(r"[:#{}\[\],&*?|>'\"%@`!]", text) or text.lower() in {"true", "false", "null"}:
            return '"' + text.replace('"', '\\"') + '"'
        return text

    @staticmethod
    def _level(level: str) -> str:
        level = str(level or "medium").lower()
        return level if level in {"informational", "low", "medium", "high", "critical"} else "medium"
