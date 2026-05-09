from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any
import uuid


class MemoryScope(str, Enum):
    SESSION = "session"
    MISSION = "mission"
    PROJECT = "project"
    USER_APPROVED = "user_approved"


class MemorySensitivity(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    SENSITIVE = "sensitive"
    SECRET_BLOCKED = "secret_blocked"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class MemoryRecord:
    content: str
    scope: MemoryScope = MemoryScope.SESSION
    sensitivity: MemorySensitivity = MemorySensitivity.INTERNAL
    record_id: str = field(default_factory=lambda: f"mem-{uuid.uuid4().hex[:12]}")
    mission_id: str | None = None
    session_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)
    updated_at: str | None = None
    trusted: bool = False
    user_approved: bool = False
    authoritative: bool = False

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["scope"] = self.scope.value
        payload["sensitivity"] = self.sensitivity.value
        return payload


@dataclass(frozen=True)
class MissionMemoryRecord:
    mission_id: str
    user_intent: str
    policy_decision: str
    risk_level: str
    approval_status: str = "not_required"
    evidence_refs: tuple[str, ...] = ()
    report_refs: tuple[str, ...] = ()
    outcome: str = "pending"
    next_step: str = ""
    record_id: str = field(default_factory=lambda: f"mission-mem-{uuid.uuid4().hex[:12]}")
    created_at: str = field(default_factory=utc_now)
    sensitivity: MemorySensitivity = MemorySensitivity.INTERNAL

    def to_memory_record(self) -> MemoryRecord:
        content = (
            f"mission_id={self.mission_id}; intent={self.user_intent}; "
            f"policy={self.policy_decision}; risk={self.risk_level}; approval={self.approval_status}; "
            f"evidence={list(self.evidence_refs)}; reports={list(self.report_refs)}; "
            f"outcome={self.outcome}; next_step={self.next_step}"
        )
        return MemoryRecord(
            record_id=self.record_id,
            mission_id=self.mission_id,
            scope=MemoryScope.MISSION,
            sensitivity=self.sensitivity,
            content=content,
            metadata={
                "user_intent": self.user_intent,
                "policy_decision": self.policy_decision,
                "risk_level": self.risk_level,
                "approval_status": self.approval_status,
                "evidence_refs": list(self.evidence_refs),
                "report_refs": list(self.report_refs),
                "outcome": self.outcome,
                "next_step": self.next_step,
            },
            trusted=False,
            authoritative=False,
        )


@dataclass(frozen=True)
class SessionSummary:
    decisions: tuple[str, ...] = ()
    risks: tuple[str, ...] = ()
    approvals: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    follow_ups: tuple[str, ...] = ()
    text: str = ""
    sensitivity: MemorySensitivity = MemorySensitivity.INTERNAL


@dataclass(frozen=True)
class ContextItem:
    content: str
    scope: MemoryScope = MemoryScope.SESSION
    sensitivity: MemorySensitivity = MemorySensitivity.INTERNAL
    reason: str = ""
    priority: int = 0
    record_id: str | None = None
    mission_id: str | None = None
    created_at: str = field(default_factory=utc_now)
    trusted: bool = False
    user_approved: bool = False


@dataclass(frozen=True)
class MemoryRetrievalResult:
    query: str
    records: tuple[MemoryRecord, ...]
    reasons: tuple[str, ...]
    limit: int

    @property
    def count(self) -> int:
        return len(self.records)

    def as_context_items(self) -> tuple[ContextItem, ...]:
        return tuple(
            ContextItem(
                content=r.content,
                scope=r.scope,
                sensitivity=r.sensitivity,
                reason=self.reasons[i] if i < len(self.reasons) else "retrieved",
                priority=50,
                record_id=r.record_id,
                mission_id=r.mission_id,
                created_at=r.created_at,
                trusted=r.trusted,
                user_approved=r.user_approved,
            )
            for i, r in enumerate(self.records)
        )
