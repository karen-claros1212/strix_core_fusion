from __future__ import annotations

import re
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class DefensiveWorkflowKind(str, Enum):
    MALWARE_TRIAGE = "malware_triage"
    SUSPICIOUS_PROCESS = "suspicious_process"
    CREDENTIAL_THEFT = "credential_theft"
    RANSOMWARE_RESPONSE = "ransomware_response"
    WEBSHELL_INVESTIGATION = "webshell_investigation"
    PHISHING_ATTACHMENT = "phishing_attachment"


@dataclass(frozen=True)
class DefensiveCommandSuggestion:
    command: str
    purpose: str
    read_only: bool = True
    dry_run: bool = True
    execution_allowed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DefensiveWorkflowPlan:
    workflow_id: str
    title: str
    summary: str
    classification: dict[str, Any]
    mitre_mappings: list[dict[str, Any]] = field(default_factory=list)
    indicators: list[dict[str, Any]] = field(default_factory=list)
    evidence: dict[str, Any] = field(default_factory=dict)
    yara_rules: list[dict[str, Any]] = field(default_factory=list)
    sigma_rules: list[dict[str, Any]] = field(default_factory=list)
    playbook: dict[str, Any] | None = None
    checklist: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    suggested_commands: list[DefensiveCommandSuggestion] = field(default_factory=list)
    memory_summary: dict[str, Any] = field(default_factory=dict)
    report_required: bool = True
    evidence_required: bool = True
    non_authoritative: bool = True
    execution_allowed: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.execution_allowed:
            raise ValueError("defensive workflows must be non-executing")
        if not self.report_required or not self.evidence_required:
            raise ValueError("defensive workflows require evidence and reports")
        for command in self.suggested_commands:
            if command.execution_allowed or not command.read_only or not command.dry_run:
                raise ValueError("suggested commands must remain read-only dry-run guidance")

    @property
    def executed(self) -> bool:
        return False

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["execution_allowed"] = False
        payload["executed"] = False
        payload["suggested_commands"] = [c.to_dict() if hasattr(c, "to_dict") else c for c in self.suggested_commands]
        return redact_obj(payload)


@dataclass(frozen=True)
class DefensiveWorkflowReport:
    report_id: str
    workflow_id: str
    executive_summary: str
    technical_report: str
    telegram_summary: str
    redacted: bool = True
    non_authoritative: bool = True
    execution_allowed: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["execution_allowed"] = False
        return redact_obj(payload)


_SECRET_PATTERNS = (
    re.compile(r"(?i)(authorization\s*:\s*bearer\s+)[A-Za-z0-9._:-]+"),
    re.compile(r"(?i)((api[_-]?key|secret[_-]?key|password|token)\s*[=:]\s*)[^\s,;'\"]+"),
    re.compile(r"\b\d{6,}:[A-Za-z0-9_-]{20,}\b"),
)


def redact_text(text: str) -> str:
    value = str(text or "")
    value = _SECRET_PATTERNS[0].sub(r"\1[REDACTED]", value)
    value = _SECRET_PATTERNS[1].sub(r"\1[REDACTED]", value)
    value = _SECRET_PATTERNS[2].sub("[REDACTED_TELEGRAM_TOKEN]", value)
    return value


def redact_obj(value: Any) -> Any:
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, item in value.items():
            key_text = str(key).lower().replace("-", "_")
            if any(term in key_text for term in ("token", "secret", "password", "api_key", "apikey", "authorization", "private_key")):
                out[key] = "[REDACTED]" if item else item
            else:
                out[key] = redact_obj(item)
        return out
    if isinstance(value, list):
        return [redact_obj(item) for item in value]
    if isinstance(value, tuple):
        return [redact_obj(item) for item in value]
    if isinstance(value, str):
        return redact_text(value)
    return value


def make_workflow_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"
