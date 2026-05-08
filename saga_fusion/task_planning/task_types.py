from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any
import uuid


class TaskCategory(str, Enum):
    READ_ONLY = "read_only"
    REPO_AUDIT = "repo_audit"
    REPORTING = "reporting"
    CLOUDOPS = "cloudops"
    FILESYSTEM = "filesystem"
    DEFENSIVE_WORKFLOW = "defensive_workflow"
    UNKNOWN = "unknown"


class TaskRisk(str, Enum):
    R0 = "R0"
    R1 = "R1"
    R2 = "R2"
    R3 = "R3"
    R4 = "R4"
    R5 = "R5"


class TaskPlanStatus(str, Enum):
    PLANNED = "planned"
    APPROVAL_REQUIRED = "approval_required"
    BLOCKED = "blocked"
    POLICY_REVIEW_REQUIRED = "policy_review_required"


@dataclass(frozen=True)
class PatternDefinition:
    pattern_id: str
    name: str
    category: TaskCategory
    action_type: str
    tool_name: str
    risk_level: TaskRisk
    keywords: tuple[str, ...]
    description: str
    requires_approval: bool = False
    blocked: bool = False
    requires_sandbox: bool = True
    reporting_tags: tuple[str, ...] = ()
    safe_modes: tuple[str, ...] = ("dry_run", "report_only")


@dataclass(frozen=True)
class TaskPlanStep:
    step_id: str
    name: str
    intent: str
    policy_gate: str
    tool_name: str = ""
    risk_level: TaskRisk = TaskRisk.R1
    requires_approval: bool = False
    blocked: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TaskPlan:
    plan_id: str
    source_text: str
    pattern_id: str
    action_type: str
    target: str
    arguments: str
    risk_level: TaskRisk
    status: TaskPlanStatus
    steps: tuple[TaskPlanStep, ...]
    approval_required: bool
    blocked: bool
    reason: str
    execution_allowed: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["risk_level"] = self.risk_level.value
        payload["status"] = self.status.value
        payload["steps"] = [
            {
                **asdict(step),
                "risk_level": step.risk_level.value,
            }
            for step in self.steps
        ]
        return payload


@dataclass(frozen=True)
class ExecutionIntent:
    intent_id: str
    plan_id: str
    tool_name: str
    action_type: str
    target: str
    risk_level: TaskRisk
    sandbox_mode: str
    dry_run: bool
    approval_required: bool
    blocked: bool
    execution_allowed: bool
    evidence_required: bool
    reason: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["risk_level"] = self.risk_level.value
        return payload

    @classmethod
    def new_id(cls) -> str:
        return f"intent-{uuid.uuid4().hex[:12]}"
