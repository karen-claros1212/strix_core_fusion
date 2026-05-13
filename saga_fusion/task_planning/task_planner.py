from __future__ import annotations

import uuid

from .execution_intent_builder import ExecutionIntentBuilder
from .pattern_registry import PatternRegistry
from .task_plan_policy import TaskPlanPolicy
from .task_types import ExecutionIntent, TaskCategory, TaskPlan, TaskPlanStep, TaskPlanStatus, TaskRisk


class TaskPlanner:
    """Clean-room deterministic task planner for Saga Fusion.

    Produces declarative plans and execution intents only. It has no method that
    executes tools, shells, browsers, CloudOps, Telegram real actions, or pentest
    operations.
    """

    def __init__(self, registry: PatternRegistry | None = None, policy: TaskPlanPolicy | None = None, intent_builder: ExecutionIntentBuilder | None = None):
        self.registry = registry or PatternRegistry()
        self.policy = policy or TaskPlanPolicy()
        self.intent_builder = intent_builder or ExecutionIntentBuilder()
        self.executed = False

    def plan(self, text: str, target: str = "", arguments: str = "", context: dict | None = None) -> TaskPlan:
        source_text = text or ""
        pattern = self.registry.match(source_text)
        decision = self.policy.decide(pattern, source_text, target=target, arguments=arguments)
        pattern_id = pattern.pattern_id if pattern else "unknown_pattern"
        action_type = pattern.action_type if pattern else "unknown"
        tool_name = decision.tool_name

        steps = [
            TaskPlanStep(
                step_id="policy_gate",
                name="MissionPolicy / DangerousActionPolicy gate",
                intent="classify_risk_and_gate",
                policy_gate="MissionPolicy+DangerousActionPolicy",
                risk_level=decision.risk_level,
                requires_approval=decision.approval_required,
                blocked=decision.blocked,
                metadata={"reason": decision.reason},
            ),
            TaskPlanStep(
                step_id="tool_route",
                name="ToolRouter route intent",
                intent="build_route_metadata_only",
                policy_gate="ToolRouter",
                tool_name=tool_name,
                risk_level=decision.risk_level,
                requires_approval=decision.approval_required,
                blocked=decision.blocked,
                metadata={"sandbox_required": decision.sandbox_required, "execution_allowed": False},
            ),
        ]
        if decision.status == TaskPlanStatus.APPROVAL_REQUIRED:
            steps.append(
                TaskPlanStep(
                    step_id="approval_intent",
                    name="R4 approval request intent",
                    intent="request_human_approval_before_any_execution",
                    policy_gate="ApprovalVerifier",
                    tool_name=tool_name,
                    risk_level=TaskRisk.R4,
                    requires_approval=True,
                    blocked=False,
                    metadata={"single_use": True, "action_hash_required": True},
                )
            )
        elif decision.status == TaskPlanStatus.BLOCKED:
            steps.append(
                TaskPlanStep(
                    step_id="blocked_intent",
                    name="R5 blocked intent",
                    intent="do_not_execute_or_approve",
                    policy_gate="MissionPolicy",
                    tool_name=tool_name,
                    risk_level=TaskRisk.R5,
                    requires_approval=False,
                    blocked=True,
                    metadata={"non_approvable": True},
                )
            )
        else:
            steps.append(
                TaskPlanStep(
                    step_id="dry_run_intent",
                    name="Sandbox dry-run/report intent",
                    intent="prepare_dry_run_or_report_only",
                    policy_gate="SandboxController",
                    tool_name=tool_name,
                    risk_level=decision.risk_level,
                    requires_approval=False,
                    blocked=decision.blocked,
                    metadata={"dry_run": True, "execute": False},
                )
            )

        report_tags = tuple(pattern.reporting_tags) if pattern else ("unknown", "policy_review")
        workflow_plan_payload = None
        cyber_playbook_payload = None
        if pattern and pattern.category == TaskCategory.DEFENSIVE_WORKFLOW:
            if pattern.tool_name.startswith("cyber_playbook:"):
                playbook_id = pattern.tool_name.split(":", 1)[1]
                cyber_playbook_payload = self._build_cyber_playbook_payload(playbook_id)
            else:
                workflow_id = pattern.tool_name.split(":", 1)[1] if ":" in pattern.tool_name else pattern.pattern_id
                workflow_plan_payload = self._build_workflow_plan_payload(workflow_id, source_text, target, arguments)
        return TaskPlan(
            plan_id=f"plan-{uuid.uuid4().hex[:12]}",
            source_text=source_text,
            pattern_id=pattern_id,
            action_type=action_type,
            target=target or self._derive_target(source_text, action_type),
            arguments=arguments or source_text,
            risk_level=decision.risk_level,
            status=decision.status,
            steps=tuple(steps),
            approval_required=decision.approval_required,
            blocked=decision.blocked,
            reason=decision.reason,
            execution_allowed=False,
            metadata={
                "tool_name": tool_name,
                "sandbox_required": decision.sandbox_required,
                "reporting_ready": True,
                "reporting_tags": report_tags,
                "clean_room": True,
                "source": "saga_fusion_task_planner",
                "context_keys": sorted((context or {}).keys()),
                "workflow_plan": workflow_plan_payload,
                "cyber_playbook": cyber_playbook_payload,
                "skill_metadata": dict(pattern.skill_metadata) if pattern else {},
            },
        )

    def build_execution_intent(self, plan: TaskPlan) -> ExecutionIntent:
        return self.intent_builder.build(plan)


    @staticmethod
    def _build_cyber_playbook_payload(playbook_id: str) -> dict | None:
        from ..cyber_knowledge import IncidentPlaybookRegistry

        playbook = IncidentPlaybookRegistry().get(playbook_id)
        if playbook is None:
            return None
        payload = playbook.to_dict()
        payload["selected_by_task_planner"] = True
        payload["execution_allowed"] = False
        return payload

    @staticmethod
    def _build_workflow_plan_payload(workflow_id: str, text: str, target: str, arguments: str) -> dict | None:
        from ..workflows import DefensiveWorkflowRegistry

        registry = DefensiveWorkflowRegistry()
        template = registry.get(workflow_id)
        if template is None:
            return None
        scope_value = target or arguments or text or "unspecified"
        inputs: dict[str, str] = {}
        for required in template.required_inputs:
            if required == "repo_path":
                inputs[required] = target or "."
            elif required == "log_path":
                inputs[required] = target or "."
            elif required == "scope":
                inputs[required] = scope_value
            elif required == "incident_summary":
                inputs[required] = text or scope_value
            else:
                inputs[required] = scope_value
        plan = template.build_plan(inputs=inputs, notes=("selected_by_task_planner", "execution_allowed_false"))
        return plan.to_dict()

    @staticmethod
    def _derive_target(text: str, action_type: str) -> str:
        normalized = " ".join((text or "").split())
        if not normalized:
            return ""
        lowered = normalized.lower()
        for prefix in (action_type.lower(), "please", "por favor"):
            if lowered.startswith(prefix):
                return normalized[len(prefix):].strip()
        return normalized
