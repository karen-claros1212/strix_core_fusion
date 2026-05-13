from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from saga_fusion.defensive_workflows import DefensiveWorkflowKind
from saga_fusion.defensive_workflows.defensive_workflow_types import redact_text


DEFENSE_STATUS_COMMAND = "defense_status"

COMMAND_TO_WORKFLOW: dict[str, str] = {
    "malware_triage": DefensiveWorkflowKind.MALWARE_TRIAGE.value,
    "ransomware_response": DefensiveWorkflowKind.RANSOMWARE_RESPONSE.value,
    "phishing_review": DefensiveWorkflowKind.PHISHING_ATTACHMENT.value,
    "webshell_investigation": DefensiveWorkflowKind.WEBSHELL_INVESTIGATION.value,
    "credential_theft_review": DefensiveWorkflowKind.CREDENTIAL_THEFT.value,
    "suspicious_process_review": DefensiveWorkflowKind.SUSPICIOUS_PROCESS.value,
}

DEFENSIVE_COMMANDS = frozenset({DEFENSE_STATUS_COMMAND, *COMMAND_TO_WORKFLOW.keys()})

_NATURAL_LANGUAGE_RULES: tuple[tuple[tuple[str, ...], str], ...] = (
    (("estado", "defensa"), DefensiveWorkflowKind.DEFENSE_STATUS.value),
    (("ransomware",), DefensiveWorkflowKind.RANSOMWARE_RESPONSE.value),
    (("adjunto", "sospechoso"), DefensiveWorkflowKind.PHISHING_ATTACHMENT.value),
    (("phishing", "adjunto"), DefensiveWorkflowKind.PHISHING_ATTACHMENT.value),
    (("triage", "malware"), DefensiveWorkflowKind.MALWARE_TRIAGE.value),
    (("malware",), DefensiveWorkflowKind.MALWARE_TRIAGE.value),
    (("robo", "credenciales"), DefensiveWorkflowKind.CREDENTIAL_THEFT.value),
    (("credenciales",), DefensiveWorkflowKind.CREDENTIAL_THEFT.value),
    (("webshell",), DefensiveWorkflowKind.WEBSHELL_INVESTIGATION.value),
    (("proceso", "sospechoso"), DefensiveWorkflowKind.SUSPICIOUS_PROCESS.value),
)


@dataclass(frozen=True)
class DefensiveCommandRequest:
    raw_text: str
    command: str | None = None
    workflow_id: str | None = None
    args: tuple[str, ...] = field(default_factory=tuple)
    source: str = "command"
    status: str = "selected"
    clarification_required: bool = False
    blocked: bool = False
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "raw_text": redact_text(self.raw_text),
            "command": self.command,
            "workflow_id": self.workflow_id,
            "args": [redact_text(arg) for arg in self.args],
            "source": self.source,
            "status": self.status,
            "clarification_required": self.clarification_required,
            "blocked": self.blocked,
            "reason": self.reason,
        }


def normalize_text(text: str) -> str:
    return " ".join(str(text or "").strip().lower().split())


def parse_defensive_command(text: str) -> DefensiveCommandRequest | None:
    raw = str(text or "").strip()
    if not raw.startswith("/"):
        return None
    parts = raw[1:].split()
    if not parts:
        return None
    command = parts[0].lower()
    args = tuple(parts[1:])
    if command == DEFENSE_STATUS_COMMAND:
        return DefensiveCommandRequest(raw_text=raw, command=command, args=args, workflow_id=None, source="command")
    workflow_id = COMMAND_TO_WORKFLOW.get(command)
    if workflow_id:
        return DefensiveCommandRequest(raw_text=raw, command=command, workflow_id=workflow_id, args=args, source="command")
    return DefensiveCommandRequest(raw_text=raw, command=command, args=args, source="command", status="blocked", blocked=True, reason="unknown_defensive_command")


def map_natural_language(text: str) -> DefensiveCommandRequest | None:
    raw = str(text or "").strip()
    if not raw or raw.startswith("/"):
        return None
    normalized = normalize_text(raw)
    # Preserve explicit Spanish mappings while keeping matching deterministic and local-only.
    for required_terms, workflow_id in _NATURAL_LANGUAGE_RULES:
        if all(re.search(r"\b" + re.escape(term) + r"\b", normalized) for term in required_terms):
            if workflow_id == DefensiveWorkflowKind.DEFENSE_STATUS.value:
                return DefensiveCommandRequest(raw_text=raw, command=DEFENSE_STATUS_COMMAND, workflow_id=None, source="natural_language")
            return DefensiveCommandRequest(raw_text=raw, workflow_id=workflow_id, source="natural_language")
    return None


def is_defensive_command(text: str) -> bool:
    request = parse_defensive_command(text)
    return bool(request and request.command in DEFENSIVE_COMMANDS)


def known_defensive_commands() -> list[str]:
    return [f"/{command}" for command in sorted(DEFENSIVE_COMMANDS)]
