from __future__ import annotations

from saga_fusion.scheduler import ScheduledJob, ScheduledJobStatus, SchedulerPolicy, SchedulerRegistry
from saga_fusion.tool_scoping import ScopedToolRouter


def test_scoped_tool_router_integration_blocks_out_of_scope_without_execution():
    policy = SchedulerPolicy(scoped_tool_router=ScopedToolRouter())
    registry = SchedulerRegistry(policy=policy)
    job = ScheduledJob(name="scope blocked", schedule="* * * * *", owner="secops", action_type="repo audit", tool_name="repo_audit")
    decision = registry.register(job, context={"toolset": "reporting"})
    assert decision.blocked is True
    assert decision.status == ScheduledJobStatus.BLOCKED
    assert decision.reason == "out_of_scope_tool_blocked"
    assert decision.evidence_metadata["tool_scope_decision"]["execution_allowed"] is False
    assert policy.scoped_tool_router.executed is False


def test_scoped_tool_router_integration_accepts_in_scope_metadata_only():
    policy = SchedulerPolicy(scoped_tool_router=ScopedToolRouter())
    registry = SchedulerRegistry(policy=policy)
    job = ScheduledJob(name="scope allowed", schedule="* * * * *", owner="secops", action_type="status", tool_name="status")
    decision = registry.register(job, context={"toolset": "reporting"})
    assert decision.accepted is True
    assert decision.status == ScheduledJobStatus.PLANNED
    assert registry.get(job.job_id).execution_allowed is False
    assert policy.scoped_tool_router.executed is False
