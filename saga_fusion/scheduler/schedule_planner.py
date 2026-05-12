from __future__ import annotations

from datetime import datetime

from .cron_validator import CronValidator
from .scheduler_registry import SchedulerRegistry
from .scheduler_types import SchedulePlan, ScheduledJob, ScheduledJobStatus


class SchedulePlanner:
    """Computes next-run metadata only; intentionally has no execute/run method."""

    def __init__(self, registry: SchedulerRegistry | None = None, cron_validator: CronValidator | None = None):
        self.registry = registry
        self.cron_validator = cron_validator or CronValidator()

    def plan_next_run(self, job_or_id: ScheduledJob | str, after: datetime | None = None) -> SchedulePlan:
        job = self._resolve(job_or_id)
        if job.cancelled or job.status == ScheduledJobStatus.CANCELLED:
            return self._plan(job, None, ScheduledJobStatus.CANCELLED, "job_cancelled_no_execution")
        if not job.enabled:
            return self._plan(job, None, job.status, "job_disabled_no_execution")
        if job.status in (ScheduledJobStatus.BLOCKED, ScheduledJobStatus.APPROVAL_REQUIRED):
            return self._plan(job, None, job.status, f"{job.status.value}_no_execution")
        next_run = self.cron_validator.next_run_after(job.schedule, after=after)
        return self._plan(job, next_run, ScheduledJobStatus.PLANNED, "next_run_planned_metadata_only")

    def _resolve(self, job_or_id: ScheduledJob | str) -> ScheduledJob:
        if isinstance(job_or_id, ScheduledJob):
            return job_or_id
        if self.registry is None:
            raise KeyError("planner has no registry")
        job = self.registry.get(job_or_id)
        if job is None:
            raise KeyError(f"unknown scheduled job: {job_or_id}")
        return job

    @staticmethod
    def _plan(job: ScheduledJob, next_run: datetime | None, status: ScheduledJobStatus, reason: str) -> SchedulePlan:
        return SchedulePlan(
            job_id=job.job_id,
            next_run_at=next_run,
            status=status,
            dry_run=True,
            execution_allowed=False,
            reason=reason,
            evidence_required=True,
            metadata={"metadata_only": True, "owner": job.owner, "schedule": job.schedule, "tool_name": job.tool_name},
        )


__all__ = ["SchedulePlanner"]
