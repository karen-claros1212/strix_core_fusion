from __future__ import annotations

from dataclasses import dataclass, asdict, field
from enum import Enum
from typing import Any


class RuleFormat(str, Enum):
    YARA = "yara"
    SIGMA = "sigma"


@dataclass(frozen=True)
class DetectionRule:
    name: str
    rule_format: RuleFormat
    content: str
    description: str
    tags: tuple[str, ...] = ()
    severity: str = "medium"
    execution_allowed: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["rule_format"] = self.rule_format.value
        return payload


class SafetyValidationError(ValueError):
    pass


FORBIDDEN_INTENT_TERMS = (
    "payload", "shellcode", "reverse shell", "bind shell", "persistence code", "autorun code",
    "exfiltrate", "exfiltration script", "credential dump", "steal cookies", "steal tokens",
    "av bypass", "edr bypass", "disable defender", "amsi bypass", "uac bypass", "exploit code",
    "download and execute", "execute malware", "run malware", "dropper code",
)


def validate_defensive_request(*parts: object) -> None:
    text = " ".join(str(p or "") for p in parts).lower()
    hits = [term for term in FORBIDDEN_INTENT_TERMS if term in text]
    if hits:
        raise SafetyValidationError(f"offensive_or_execution_request_rejected: {', '.join(hits[:3])}")
