from __future__ import annotations

from saga_fusion.policy import DangerousActionPolicy
from saga_fusion.tool_routing.tool_routing_types import ToolRisk
from saga_fusion.tool_scoping import ScopedToolRouter

from .cron_validator import CronValidationError, CronValidator
from .scheduler_types import ScheduledJob, ScheduledJobStatus, SchedulerPolicyDecision, SchedulerRisk


class SchedulerPolicy:
    """Policy gate for dry-run scheduled-job metadata. It grants no execution."""

    def __init__(self, max_timeout_seconds: int = 3600, cron_validator: CronValidator | None = None, dangerous_policy: DangerousActionPolicy | None = None, scoped_tool_router: ScopedToolRouter | None = None):
        self.max_timeout_seconds = max_timeout_seconds
        self.cron_validator = cron_validator or CronValidator()
        self.dangerous_policy = dangerous_policy or DangerousActionPolicy()
        self.scoped_tool_router = scoped_tool_router

    def decide(self, job: ScheduledJob, context: dict | None = None) -> SchedulerPolicyDecision:
        evidence = {
            "metadata_only": True,
            "dry_run": True,
            "execution_allowed": False,
            "owner": job.owner,
            "schedule": job.schedule,
            "tool_name": job.tool_name,
            "timeout_seconds": job.timeout_seconds,
        }
        if job.execution_allowed:
            return self._decision(False, True, False, ScheduledJobStatus.BLOCKED, "execution_allowed_true_denied", job, evidence)
        if not job.dry_run:
            return self._decision(False, True, False, ScheduledJobStatus.BLOCKED, "non_dry_run_scheduler_denied", job, evidence)
        if not job.owner:
            return self._decision(False, True, False, ScheduledJobStatus.BLOCKED, "owner_required", job, evidence)
        if job.timeout_seconds <= 0 or job.timeout_seconds > self.max_timeout_seconds:
            evidence["max_timeout_seconds"] = self.max_timeout_seconds
            return self._decision(False, True, False, ScheduledJobStatus.BLOCKED, "timeout_out_of_bounds", job, evidence)
        try:
            self.cron_validator.validate(job.schedule)
        except CronValidationError as exc:
            evidence["cron_error"] = str(exc)
            return self._decision(False, True, False, ScheduledJobStatus.BLOCKED, "invalid_cron_expression", job, evidence)
        if job.cancelled:
            return self._decision(False, True, False, ScheduledJobStatus.CANCELLED, "job_cancelled", job, evidence)

        dangerous_text = " ".join([job.action_type, job.tool_name, job.target, str(job.arguments), str(job.metadata)])
        dangerous = self.dangerous_policy.evaluate(dangerous_text)
        if dangerous.blocked:
            evidence["dangerous_action"] = {"reason": dangerous.reason, "risk_level": dangerous.risk_level, "patterns": list(dangerous.matched_patterns)}
            return self._decision(False, True, False, ScheduledJobStatus.BLOCKED, "risk_r5_or_destructive_job_blocked", job, evidence, risk=SchedulerRisk.R5)
        if job.risk_level == SchedulerRisk.R5:
            return self._decision(False, True, False, ScheduledJobStatus.BLOCKED, "risk_r5_blocked", job, evidence)
        if job.risk_level == SchedulerRisk.R4 or dangerous.approval_required:
            if dangerous.approval_required:
                evidence["dangerous_action"] = {"reason": dangerous.reason, "risk_level": dangerous.risk_level, "patterns": list(dangerous.matched_patterns)}
            return self._decision(False, False, True, ScheduledJobStatus.APPROVAL_REQUIRED, "risk_r4_requires_approval", job, evidence, risk=SchedulerRisk.R4)

        if self.scoped_tool_router is not None:
            request = {"tool_name": job.tool_name, "action_type": job.action_type, "target": job.target, "arguments": job.arguments}
            decision = self.scoped_tool_router.route_tool_request(request, context=context or {})
            evidence["tool_scope_decision"] = {
                "reason": decision.reason,
                "blocked": decision.blocked,
                "approval_required": decision.approval_required,
                "execution_allowed": False,
            }
            if decision.blocked:
                return self._decision(False, True, False, ScheduledJobStatus.BLOCKED, decision.reason, job, evidence, risk=self._from_tool_risk(decision.risk_level))
            if decision.approval_required:
                return self._decision(False, False, True, ScheduledJobStatus.APPROVAL_REQUIRED, decision.reason, job, evidence, risk=self._from_tool_risk(decision.risk_level))

        return self._decision(True, False, False, ScheduledJobStatus.PLANNED, "accepted_dry_run_metadata_only", job, evidence)

    @staticmethod
    def _from_tool_risk(risk: ToolRisk) -> SchedulerRisk:
        try:
            return SchedulerRisk(risk.value)
        except ValueError:
            return SchedulerRisk.R4

    @staticmethod
    def _decision(accepted: bool, blocked: bool, approval_required: bool, status: ScheduledJobStatus, reason: str, job: ScheduledJob, evidence: dict, risk: SchedulerRisk | None = None) -> SchedulerPolicyDecision:
        return SchedulerPolicyDecision(accepted, blocked, approval_required, status, reason, job.job_id, risk or job.risk_level, evidence)


__all__ = ["SchedulerPolicy"]
