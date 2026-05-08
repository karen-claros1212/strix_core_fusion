from saga_fusion.tool_routing import ToolExecutionPlan, ToolRisk


def test_execution_plan_is_structured_and_does_not_execute():
    plan = ToolExecutionPlan(
        tool_name='repo_audit', action='audit', args={'target':'repo'}, risk_level=ToolRisk.R3,
        sandbox_mode='dry_run', dry_run=True, approval_required=False, evidence_required=True,
        execution_allowed=True,
    )
    assert plan.tool_name == 'repo_audit'
    assert plan.dry_run is True
    assert plan.evidence_required is True
    assert not hasattr(plan, 'execute')
