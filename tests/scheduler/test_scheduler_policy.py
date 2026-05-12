from __future__ import annotations

from datetime import datetime, timezone
import pytest

from saga_fusion.scheduler import SchedulePlanner, ScheduledJob, ScheduledJobStatus, SchedulerPolicy, SchedulerRegistry, SchedulerRisk


def test_valid_dry_run_job_accepted_and_next_run_planned_only():
    registry = SchedulerRegistry()
    job = ScheduledJob(name="daily status", schedule="*/15 * * * *", owner="secops", action_type="status", tool_name="status")
    decision = registry.register(job)
    assert decision.accepted is True
    assert decision.reason == "accepted_dry_run_metadata_only"
    assert decision.evidence_metadata["execution_allowed"] is False

    stored = registry.get(job.job_id)
    assert stored is not None
    assert stored.dry_run is True
    assert stored.execution_allowed is False
    assert stored.status == ScheduledJobStatus.PLANNED

    plan = SchedulePlanner(registry).plan_next_run(job.job_id, after=datetime(2026, 5, 12, 0, 0, tzinfo=timezone.utc))
    assert plan.next_run_at == datetime(2026, 5, 12, 0, 15, tzinfo=timezone.utc)
    assert plan.dry_run is True
    assert plan.execution_allowed is False


def test_invalid_cron_rejected():
    registry = SchedulerRegistry()
    job = ScheduledJob(name="bad", schedule="61 * * * *", owner="secops", action_type="status", tool_name="status")
    decision = registry.register(job)
    assert decision.blocked is True
    assert decision.status == ScheduledJobStatus.BLOCKED
    assert decision.reason == "invalid_cron_expression"


@pytest.mark.parametrize("kwargs", [{"execution_allowed": True}, {"dry_run": False}])
def test_execution_allowed_cannot_be_enabled_and_dry_run_required(kwargs):
    with pytest.raises(ValueError):
        ScheduledJob(name="unsafe", schedule="* * * * *", owner="secops", action_type="status", tool_name="status", **kwargs)


def test_owner_required():
    with pytest.raises(ValueError, match="owner"):
        ScheduledJob(name="orphan", schedule="* * * * *", owner="", action_type="status", tool_name="status")


def test_timeout_bounded_by_policy():
    policy = SchedulerPolicy(max_timeout_seconds=60)
    registry = SchedulerRegistry(policy=policy)
    job = ScheduledJob(name="slow", schedule="* * * * *", owner="secops", action_type="status", tool_name="status", timeout_seconds=61)
    decision = registry.register(job)
    assert decision.blocked is True
    assert decision.reason == "timeout_out_of_bounds"
    assert decision.evidence_metadata["max_timeout_seconds"] == 60


def test_cancel_job_sets_cancelled_and_no_next_run_execution():
    registry = SchedulerRegistry()
    job = ScheduledJob(name="cancel", schedule="* * * * *", owner="secops", action_type="status", tool_name="status")
    registry.register(job)
    cancelled = registry.cancel(job.job_id)
    assert cancelled.cancelled is True
    assert cancelled.enabled is False
    assert cancelled.status == ScheduledJobStatus.CANCELLED
    assert cancelled.execution_allowed is False

    plan = SchedulePlanner(registry).plan_next_run(job.job_id)
    assert plan.status == ScheduledJobStatus.CANCELLED
    assert plan.next_run_at is None
    assert plan.execution_allowed is False


def test_r4_job_requires_approval():
    registry = SchedulerRegistry()
    job = ScheduledJob(name="cloud plan", schedule="0 3 * * *", owner="secops", action_type="create vps", tool_name="cloudops_plan", risk_level=SchedulerRisk.R4)
    decision = registry.register(job)
    assert decision.approval_required is True
    assert decision.blocked is False
    assert decision.status == ScheduledJobStatus.APPROVAL_REQUIRED
    assert registry.get(job.job_id).execution_allowed is False


def test_r5_and_destructive_job_blocked():
    registry = SchedulerRegistry()
    r5 = ScheduledJob(name="delete backups", schedule="0 4 * * *", owner="secops", action_type="delete backups", tool_name="backup_plan", risk_level=SchedulerRisk.R5)
    decision = registry.register(r5)
    assert decision.blocked is True
    assert decision.status == ScheduledJobStatus.BLOCKED

    destructive = ScheduledJob(name="destroy server", schedule="0 5 * * *", owner="secops", action_type="destroy server", tool_name="cloudops_plan", risk_level=SchedulerRisk.R3)
    decision2 = registry.register(destructive)
    assert decision2.blocked is True
    assert decision2.risk_level == SchedulerRisk.R5


def test_no_real_execution_method_exists():
    planner = SchedulePlanner()
    registry = SchedulerRegistry()
    assert not hasattr(planner, "execute")
    assert not hasattr(planner, "run")
    assert not hasattr(registry, "execute")
    assert not hasattr(registry, "run")


def test_evidence_metadata_redacted_safe():
    job = ScheduledJob(
        name="redact",
        schedule="* * * * *",
        owner="secops",
        action_type="status",
        tool_name="status",
        evidence_ref="Authorization: Bearer abc123",
        metadata={"token": "abc123", "note": "api_key=secret-value"},
        arguments={"password": "secret", "safe": "ok"},
    )
    assert "abc123" not in job.evidence_ref
    assert job.metadata["token"] == "[REDACTED]"
    assert "secret-value" not in job.metadata["note"]
    assert job.arguments["password"] == "[REDACTED]"
