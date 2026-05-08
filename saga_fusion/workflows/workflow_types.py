from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class WorkflowCategory(str, Enum):
    REPOSITORY_AUDIT = "repository_audit"
    SECRET_AUDIT = "secret_audit"
    DEPENDENCY_AUDIT = "dependency_audit"
    DOCKER_AUDIT = "docker_audit"
    CONFIGURATION_AUDIT = "configuration_audit"
    LOG_REVIEW = "log_review"
    HARDENING_PLAN = "hardening_plan"
    INCIDENT_RESPONSE = "incident_response"


class WorkflowRisk(str, Enum):
    R1 = "R1"
    R2 = "R2"
    R3 = "R3"
    R4 = "R4"
    R5 = "R5"


@dataclass(frozen=True)
class WorkflowStep:
    step_id: str
    name: str
    description: str
    evidence_keys: tuple[str, ...] = ()
    policy_gates: tuple[str, ...] = (
        "PromptSecurity",
        "MissionPolicy",
        "DangerousActionPolicy",
        "ToolRouter",
        "ApprovalVerifier",
        "SandboxController",
        "EvidenceLogger",
        "Reporting",
    )
    execution_allowed: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class WorkflowTemplate:
    workflow_id: str
    name: str
    category: WorkflowCategory
    default_risk: WorkflowRisk
    allowed_mode: str
    required_inputs: tuple[str, ...]
    steps: tuple[WorkflowStep, ...]
    evidence_required: bool = True
    report_required: bool = True
    execution_allowed: bool = False
    description: str = ""
    tags: tuple[str, ...] = ()

    def build_plan(self, inputs: dict[str, Any] | None = None, evidence: dict[str, Any] | None = None, notes: tuple[str, ...] = ()) -> "WorkflowPlan":
        payload = dict(inputs or {})
        missing = tuple(key for key in self.required_inputs if key not in payload or payload.get(key) in (None, ""))
        return WorkflowPlan(
            plan_id=f"workflow-plan-{uuid.uuid4().hex[:12]}",
            workflow_id=self.workflow_id,
            name=self.name,
            category=self.category,
            risk=self.default_risk,
            allowed_mode=self.allowed_mode,
            required_inputs=self.required_inputs,
            missing_inputs=missing,
            steps=self.steps,
            evidence_required=self.evidence_required,
            report_required=self.report_required,
            execution_allowed=False,
            inputs=_safe_inputs(payload),
            evidence=evidence or {},
            notes=notes,
        )


@dataclass(frozen=True)
class WorkflowPlan:
    plan_id: str
    workflow_id: str
    name: str
    category: WorkflowCategory
    risk: WorkflowRisk
    allowed_mode: str
    required_inputs: tuple[str, ...]
    missing_inputs: tuple[str, ...]
    steps: tuple[WorkflowStep, ...]
    evidence_required: bool
    report_required: bool
    execution_allowed: bool = False
    inputs: dict[str, Any] = field(default_factory=dict)
    evidence: dict[str, Any] = field(default_factory=dict)
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["category"] = self.category.value
        payload["risk"] = self.risk.value
        payload["steps"] = [asdict(step) for step in self.steps]
        payload["execution_allowed"] = False
        return payload


@dataclass(frozen=True)
class WorkflowResult:
    workflow_id: str
    plan: WorkflowPlan
    executed: bool = False
    execution_allowed: bool = False
    report: str = ""
    evidence: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "plan": self.plan.to_dict(),
            "executed": False,
            "execution_allowed": False,
            "report": self.report,
            "evidence": self.evidence,
        }


def workflow_step(step_id: str, name: str, description: str, evidence_keys: tuple[str, ...] = (), **metadata: Any) -> WorkflowStep:
    return WorkflowStep(step_id=step_id, name=name, description=description, evidence_keys=evidence_keys, metadata=metadata, execution_allowed=False)


def list_text_files(root: str | Path, names: tuple[str, ...] | None = None) -> list[Path]:
    base = Path(root)
    if not base.exists() or not base.is_dir():
        return []
    skip_parts = {".git", "__pycache__", ".pytest_cache", "node_modules", ".venv", "venv"}
    out: list[Path] = []
    for path in base.rglob("*"):
        if any(part in skip_parts for part in path.parts):
            continue
        if not path.is_file():
            continue
        if names is not None and path.name not in names:
            continue
        if path.stat().st_size > 256_000:
            continue
        out.append(path)
    return sorted(out)


def read_small(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _safe_inputs(inputs: dict[str, Any]) -> dict[str, Any]:
    safe = {}
    for key, value in inputs.items():
        lower = str(key).lower()
        if any(word in lower for word in ("token", "secret", "password", "key")):
            safe[key] = "[REDACTED]"
        else:
            safe[key] = str(value) if isinstance(value, Path) else value
    return safe
