from __future__ import annotations

from .task_types import ExecutionIntent, TaskPlan, TaskPlanStatus


class ExecutionIntentBuilder:
    """Build non-executing execution intents from task plans."""

    def build(self, plan: TaskPlan) -> ExecutionIntent:
        tool_name = plan.steps[-1].tool_name if plan.steps else plan.metadata.get("tool_name", "unknown")
        return ExecutionIntent(
            intent_id=ExecutionIntent.new_id(),
            plan_id=plan.plan_id,
            tool_name=tool_name or plan.metadata.get("tool_name", "unknown"),
            action_type=plan.action_type,
            target=plan.target,
            risk_level=plan.risk_level,
            sandbox_mode="blocked" if plan.blocked else ("dry_run" if plan.metadata.get("sandbox_required", True) else "not_required"),
            dry_run=True,
            approval_required=plan.approval_required,
            blocked=plan.blocked,
            execution_allowed=False,
            evidence_required=True,
            reason=plan.reason,
            metadata={
                "pattern_id": plan.pattern_id,
                "status": plan.status.value,
                "reporting_ready": bool(plan.metadata.get("reporting_ready")),
                "requires_policy_gate": plan.status in {TaskPlanStatus.APPROVAL_REQUIRED, TaskPlanStatus.BLOCKED, TaskPlanStatus.POLICY_REVIEW_REQUIRED},
            },
        )
