from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ApprovalStatus(str, Enum):
    PENDING = 'PENDING'
    APPROVED = 'APPROVED'
    DENIED = 'DENIED'
    EXPIRED = 'EXPIRED'
    INVALID_HASH = 'INVALID_HASH'
    USED = 'USED'
    BLOCKED = 'BLOCKED'


class ApprovalRiskLevel(str, Enum):
    R0 = 'R0'
    R1 = 'R1'
    R2 = 'R2'
    R3 = 'R3'
    R4 = 'R4'
    R5 = 'R5'


IRREVERSIBLE_APPROVAL_STATUSES = frozenset({
    ApprovalStatus.APPROVED,
    ApprovalStatus.DENIED,
    ApprovalStatus.EXPIRED,
    ApprovalStatus.INVALID_HASH,
    ApprovalStatus.USED,
    ApprovalStatus.BLOCKED,
})


@dataclass
class ApprovalRequest:
    approval_id: str
    mission_id: str
    action_hash: str
    canonical_action: str
    risk_level: ApprovalRiskLevel
    requested_by: str
    created_at: float
    expires_at: float
    reason: str
    summary: str
    rollback_plan: str
    before_state: str
    evidence_ref: str
    used: bool = False
    status: ApprovalStatus = ApprovalStatus.PENDING

    def is_expired(self, now: float) -> bool:
        """Return True at or after expiry; approvals are not valid at expires_at."""
        return float(now) >= float(self.expires_at)

    def seconds_until_expiry(self, now: float) -> float:
        return max(0.0, float(self.expires_at) - float(now))

    @property
    def is_terminal(self) -> bool:
        return self.used or self.status in IRREVERSIBLE_APPROVAL_STATUSES


@dataclass(frozen=True)
class ApprovalDecision:
    allowed: bool
    status: ApprovalStatus
    reason: str
    approval_id: str | None = None
    evidence: dict = field(default_factory=dict)
