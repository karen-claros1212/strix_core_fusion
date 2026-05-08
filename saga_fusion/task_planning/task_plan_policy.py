from __future__ import annotations

from dataclasses import dataclass

from .task_types import PatternDefinition, TaskPlanStatus, TaskRisk
from typing import Any


@dataclass(frozen=True)
class TaskPlanPolicyDecision:
    risk_level: TaskRisk
    status: TaskPlanStatus
    approval_required: bool
    blocked: bool
    reason: str
    tool_name: str
    sandbox_required: bool
    execution_allowed: bool = False


class TaskPlanPolicy:
    """Policy adapter for declarative plans.

    It asks the existing authoritative controls for risk/routing decisions and
    never grants execution rights by itself.
    """

    def __init__(self, mission_policy: Any | None = None, tool_router: Any | None = None, dangerous_policy: Any | None = None):
        from ..policy import DangerousActionPolicy
        from ..telegram.mission_policy import MissionPolicy
        from ..tool_routing import ToolRouter

        self.mission_policy = mission_policy or MissionPolicy()
        self.tool_router = tool_router or ToolRouter()
        self.dangerous_policy = dangerous_policy or DangerousActionPolicy()

    def decide(self, pattern: PatternDefinition | None, text: str, target: str = "", arguments: str = "") -> TaskPlanPolicyDecision:
        if pattern is None:
            return TaskPlanPolicyDecision(
                risk_level=TaskRisk.R1,
                status=TaskPlanStatus.POLICY_REVIEW_REQUIRED,
                approval_required=False,
                blocked=True,
                reason="unknown_pattern_requires_mission_policy_and_tool_router_review",
                tool_name="unknown",
                sandbox_required=True,
                execution_allowed=False,
            )

        dangerous = self.dangerous_policy.evaluate(" ".join([text or "", target or "", arguments or ""]))
        from ..telegram.telegram_types import MissionRequest

        request = MissionRequest(action_type=pattern.action_type, target=target, arguments=arguments, raw_text=text)
        mission_risk = self.mission_policy.classify_risk(request)
        route = self.tool_router.route_tool_request(request)

        mission_task_risk = self._from_mission_risk(mission_risk)
        route_task_risk = TaskRisk(route.risk_level.value)
        safe_known_pattern = pattern.risk_level in {TaskRisk.R0, TaskRisk.R1, TaskRisk.R2, TaskRisk.R3} and not dangerous.approval_required and not dangerous.blocked
        if safe_known_pattern:
            # Known safe dry-run/report patterns remain declarative unless the
            # dangerous-action layer found an actual R4/R5 condition. This avoids
            # generic verbs such as "run" upgrading repo-audit dry-runs to R4.
            risk = self._max_risk(pattern.risk_level, route_task_risk if route.blocked else pattern.risk_level)
        else:
            risk = self._max_risk(pattern.risk_level, mission_task_risk, route_task_risk)
        blocked = pattern.blocked or dangerous.blocked or (False if safe_known_pattern else self.mission_policy.is_blocked(mission_risk)) or route.blocked or risk == TaskRisk.R5
        approval_required = (pattern.requires_approval or dangerous.approval_required or (False if safe_known_pattern else self.mission_policy.requires_approval(mission_risk)) or route.approval_required or risk == TaskRisk.R4) and not blocked

        if blocked:
            status = TaskPlanStatus.BLOCKED
            reason = dangerous.reason or route.reason or "risk_r5_blocked"
        elif approval_required:
            status = TaskPlanStatus.APPROVAL_REQUIRED
            reason = dangerous.reason or route.reason or "risk_r4_approval_required"
        else:
            status = TaskPlanStatus.PLANNED
            reason = route.reason or "planned_dry_run_only"

        return TaskPlanPolicyDecision(
            risk_level=risk,
            status=status,
            approval_required=approval_required,
            blocked=blocked,
            reason=reason,
            tool_name=route.tool_name if route.tool_name != "unknown" else pattern.tool_name,
            sandbox_required=pattern.requires_sandbox or route.sandbox_required,
            execution_allowed=False,
        )

    @staticmethod
    def _from_mission_risk(risk: Any) -> TaskRisk:
        return TaskRisk[risk.name]

    @staticmethod
    def _max_risk(*risks: TaskRisk) -> TaskRisk:
        ordered = {risk: idx for idx, risk in enumerate(TaskRisk)}
        return max(risks, key=lambda risk: ordered[risk])
