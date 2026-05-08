from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ToolCategory(str, Enum):
    READ_ONLY = 'read_only'
    FILESYSTEM = 'filesystem'
    NETWORK = 'network'
    CLOUDOPS = 'cloudops'
    REPO_AUDIT = 'repo_audit'
    LLM_ONLY = 'llm_only'
    REPORTING = 'reporting'
    UNKNOWN = 'unknown'


class ToolRisk(str, Enum):
    R0 = 'R0'
    R1 = 'R1'
    R2 = 'R2'
    R3 = 'R3'
    R4 = 'R4'
    R5 = 'R5'


@dataclass(frozen=True)
class ToolMetadata:
    name: str
    category: ToolCategory
    default_risk: ToolRisk
    requires_sandbox: bool
    requires_approval: bool
    allowed_modes: tuple[str, ...]
    description: str


@dataclass(frozen=True)
class ToolRouteDecision:
    allowed: bool
    blocked: bool
    approval_required: bool
    risk_level: ToolRisk
    tool_name: str
    category: ToolCategory
    route: str
    sandbox_required: bool
    reason: str
    evidence_metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class ToolExecutionPlan:
    tool_name: str
    action: str
    args: dict
    risk_level: ToolRisk
    sandbox_mode: str
    dry_run: bool
    approval_required: bool
    evidence_required: bool
    execution_allowed: bool
