from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class SkillRiskLevel(str, Enum):
    R0 = "R0"
    R1 = "R1"
    R2 = "R2"
    R3 = "R3"
    R4 = "R4"
    R5 = "R5"


class SkillPolicyStatus(str, Enum):
    ALLOWED = "allowed"
    APPROVAL_REQUIRED = "approval_required"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class SkillPolicyDecision:
    allowed: bool
    blocked: bool
    approval_required: bool
    status: SkillPolicyStatus
    reason: str
    skill_name: str
    risk_level: SkillRiskLevel
    evidence_metadata: dict = field(default_factory=dict)


__all__ = ["SkillRiskLevel", "SkillPolicyStatus", "SkillPolicyDecision"]
