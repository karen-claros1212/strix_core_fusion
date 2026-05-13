from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from saga_fusion.defensive_workflows.defensive_workflow_types import redact_obj, redact_text


@dataclass(frozen=True)
class DefensiveLabMode:
    """Safety envelope for Phase 10C Telegram defensive workflows."""

    lab_mode: bool = True
    execution_allowed: bool = False
    evidence_required: bool = True
    report_required: bool = True
    non_authoritative: bool = True
    real_telegram_used: bool = False
    real_tool_execution: bool = False
    malware_executed: bool = False
    attachment_executed: bool = False
    attachment_processed: bool = False
    sample_downloaded: bool = False
    offensive_payload_created: bool = False
    webshell_generated: bool = False
    external_pentest: bool = False
    cloudops_used: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


DEFAULT_LAB_MODE = DefensiveLabMode()


def apply_lab_mode(payload: dict[str, Any] | None = None, *, artifact_ref: str | None = None) -> dict[str, Any]:
    """Return a redacted payload with immutable lab/evidence-only flags applied."""

    safe = redact_obj(dict(payload or {}))
    safe.update(DEFAULT_LAB_MODE.to_dict())
    safe["executed"] = False
    safe["artifact_ref"] = redact_text(artifact_ref or safe.get("artifact_ref") or "telegram:defensive-lab-report")
    return safe


def assert_lab_mode(payload: dict[str, Any]) -> bool:
    """Validate that a response cannot represent real-world execution."""

    checks = apply_lab_mode(payload)
    required_true = ("lab_mode", "evidence_required", "report_required", "non_authoritative")
    required_false = (
        "execution_allowed",
        "executed",
        "real_telegram_used",
        "real_tool_execution",
        "malware_executed",
        "attachment_executed",
        "attachment_processed",
        "sample_downloaded",
        "offensive_payload_created",
        "webshell_generated",
        "external_pentest",
        "cloudops_used",
    )
    return all(checks.get(key) is True for key in required_true) and all(checks.get(key) is False for key in required_false)
