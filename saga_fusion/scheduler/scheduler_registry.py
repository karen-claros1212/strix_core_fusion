from __future__ import annotations

from dataclasses import replace

from .scheduler_policy import SchedulerPolicy
from .scheduler_types import ScheduledJob, ScheduledJobStatus, SchedulerPolicyDecision


class SchedulerRegistry:
    """In-memory registry for planned scheduled-job metadata; no OS cron side effects."""

    def __init__(self, policy: SchedulerPolicy | None = None):
        self.policy = policy or SchedulerPolicy()
        self._jobs: dict[str, ScheduledJob] = {}
        self._decisions: dict[str, SchedulerPolicyDecision] = {}

    def register(self, job: ScheduledJob, context: dict | None = None) -> SchedulerPolicyDecision:
        if job.job_id in self._jobs:
            raise ValueError(f"duplicate scheduled job: {job.job_id}")
        decision = self.policy.decide(job, context=context)
        governed = replace(job, status=decision.status, enabled=job.enabled and decision.status == ScheduledJobStatus.PLANNED, execution_allowed=False, dry_run=True)
        self._jobs[job.job_id] = governed
        self._decisions[job.job_id] = decision
        return decision

    def get(self, job_id: str) -> ScheduledJob | None:
        return self._jobs.get(str(job_id or "").strip())

    def decision_for(self, job_id: str) -> SchedulerPolicyDecision | None:
        return self._decisions.get(str(job_id or "").strip())

    def list_jobs(self) -> list[ScheduledJob]:
        return list(self._jobs.values())

    def cancel(self, job_id: str) -> ScheduledJob:
        key = str(job_id or "").strip()
        job = self._jobs.get(key)
        if job is None:
            raise KeyError(f"unknown scheduled job: {job_id}")
        cancelled = job.cancelled_copy()
        self._jobs[key] = cancelled
        self._decisions[key] = SchedulerPolicyDecision(False, True, False, ScheduledJobStatus.CANCELLED, "job_cancelled", key, cancelled.risk_level, {"metadata_only": True, "dry_run": True, "execution_allowed": False})
        return cancelled


__all__ = ["SchedulerRegistry"]
