from __future__ import annotations

from .workflow_types import WorkflowCategory, WorkflowPlan, WorkflowRisk, WorkflowTemplate, workflow_step


def hardening_plan_template() -> WorkflowTemplate:
    return WorkflowTemplate(
        workflow_id="hardening_plan",
        name="Hardening Plan",
        category=WorkflowCategory.HARDENING_PLAN,
        default_risk=WorkflowRisk.R3,
        allowed_mode="plan_only",
        required_inputs=("scope",),
        description="Create baseline controls, prioritized recommendations, implementation steps, and rollback plan; no execution.",
        tags=("hardening", "plan_only", "rollback"),
        steps=(
            workflow_step("baseline_controls", "Baseline controls", "Document current control baseline and assumptions.", ("baseline_controls",)),
            workflow_step("prioritized_recommendations", "Prioritized recommendations", "Rank hardening recommendations by impact and safety.", ("prioritized_recommendations",)),
            workflow_step("implementation_steps", "Implementation steps", "Describe manual implementation steps for approved future changes.", ("implementation_steps",)),
            workflow_step("rollback_plan", "Rollback plan", "Define rollback and validation approach before any future execution.", ("rollback_plan",)),
            workflow_step("no_execution", "No execution", "Do not apply changes automatically.", ("execution_allowed",)),
        ),
        execution_allowed=False,
    )


def generate_hardening_plan(scope: str, **inputs) -> WorkflowPlan:
    evidence = {
        "baseline_controls": ["PromptSecurity", "MissionPolicy", "DangerousActionPolicy", "ToolRouter", "ApprovalVerifier", "SandboxController", "EvidenceLogger", "Reporting"],
        "prioritized_recommendations": ["P1: preserve execution_allowed=False", "P2: expand evidence coverage", "P3: review manual hardening tasks before change"],
        "implementation_steps": ["Draft change", "Run tests", "Human approval", "Apply in controlled window"],
        "rollback_plan": ["Capture before-state", "Keep reversible patch", "Run validation", "Revert if regression occurs"],
        "execution_allowed": False,
    }
    return hardening_plan_template().build_plan(inputs={"scope": scope, **inputs}, evidence=evidence, notes=("no_real_actions", "no_auto_remediation"))
