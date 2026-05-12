from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
from typing import Any
import re
import uuid


_SECRET_PATTERNS = (
    re.compile(r"(authorization\s*[:=]\s*bearer\s+)[^\s,;]+", re.I),
    re.compile(r"(api[_-]?key\s*[:=]\s*)[^\s,;]+", re.I),
    re.compile(r"(token\s*[:=]\s*)[^\s,;]+", re.I),
    re.compile(r"(password\s*[:=]\s*)[^\s,;]+", re.I),
)


class ScheduledJobStatus(str, Enum):
    PLANNED = "planned"
    APPROVAL_REQUIRED = "approval_required"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class SchedulerRisk(str, Enum):
    R0 = "R0"
    R1 = "R1"
    R2 = "R2"
    R3 = "R3"
    R4 = "R4"
    R5 = "R5"


@dataclass(frozen=True)
class ScheduledJob:
    """Declarative scheduled-job metadata; never an executable cron job."""

    name: str
    schedule: str
    owner: str
    action_type: str
    tool_name: str = "status"
    target: str = ""
    arguments: dict[str, Any] = field(default_factory=dict)
    risk_level: SchedulerRisk | str = SchedulerRisk.R1
    timeout_seconds: int = 300
    enabled: bool = True
    dry_run: bool = True
    execution_allowed: bool = False
    evidence_ref: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    job_id: str = field(default_factory=lambda: f"sched-{uuid.uuid4().hex[:12]}")
    status: ScheduledJobStatus = ScheduledJobStatus.PLANNED
    cancelled: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", str(self.name or "").strip())
        object.__setattr__(self, "schedule", str(self.schedule or "").strip())
        object.__setattr__(self, "owner", str(self.owner or "").strip())
        object.__setattr__(self, "action_type", str(self.action_type or "").strip().lower())
        object.__setattr__(self, "tool_name", str(self.tool_name or "").strip().lower())
        risk = self.risk_level if isinstance(self.risk_level, SchedulerRisk) else SchedulerRisk(str(self.risk_level or "R4"))
        object.__setattr__(self, "risk_level", risk)
        object.__setattr__(self, "metadata", redact_metadata(self.metadata))
        object.__setattr__(self, "arguments", redact_metadata(self.arguments))
        object.__setattr__(self, "evidence_ref", redact_text(self.evidence_ref))
        if self.execution_allowed:
            raise ValueError("scheduled jobs cannot set execution_allowed=True")
        if not self.dry_run:
            raise ValueError("scheduled jobs must remain dry_run=True")
        if not self.owner:
            raise ValueError("scheduled job owner is required")
        if not self.name:
            raise ValueError("scheduled job name is required")
        if not self.schedule:
            raise ValueError("scheduled job schedule is required")

    def cancelled_copy(self) -> "ScheduledJob":
        return replace(self, enabled=False, cancelled=True, status=ScheduledJobStatus.CANCELLED, execution_allowed=False, dry_run=True)


@dataclass(frozen=True)
class SchedulerPolicyDecision:
    accepted: bool
    blocked: bool
    approval_required: bool
    status: ScheduledJobStatus
    reason: str
    job_id: str
    risk_level: SchedulerRisk
    evidence_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SchedulePlan:
    job_id: str
    next_run_at: datetime | None
    status: ScheduledJobStatus
    dry_run: bool = True
    execution_allowed: bool = False
    reason: str = "planned_metadata_only"
    evidence_required: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


def redact_text(value: Any) -> str:
    text = str(value or "")
    for pattern in _SECRET_PATTERNS:
        text = pattern.sub(lambda m: f"{m.group(1)}[REDACTED]", text)
    return text


def redact_metadata(value: Any) -> Any:
    if isinstance(value, dict):
        redacted = {}
        for key, item in value.items():
            key_s = str(key)
            if any(marker in key_s.lower() for marker in ("token", "password", "secret", "api_key", "apikey", "authorization")):
                redacted[key_s] = "[REDACTED]"
            else:
                redacted[key_s] = redact_metadata(item)
        return redacted
    if isinstance(value, (list, tuple, set)):
        return type(value)(redact_metadata(item) for item in value)
    if isinstance(value, str):
        return redact_text(value)
    return value


__all__ = ["ScheduledJob", "ScheduledJobStatus", "SchedulerRisk", "SchedulerPolicyDecision", "SchedulePlan", "redact_metadata", "redact_text"]
