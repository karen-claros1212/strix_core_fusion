from saga_fusion.tool_routing import ToolRouter


def test_router_builds_repo_audit_dry_run_plan():
    router = ToolRouter()
    req = {'action':'repo audit dry-run','target':'repo'}
    decision = router.route_tool_request(req)
    plan = router.build_execution_plan(decision, req)
    assert decision.allowed is True
    assert decision.sandbox_required is True
    assert plan.tool_name == 'repo_audit'
    assert plan.dry_run is True
    assert plan.evidence_required is True
    assert router.executed is False
    assert decision.evidence_metadata


def test_router_builds_approval_plan_for_create_vps_and_blocks_delete():
    router = ToolRouter()
    create = router.route_tool_request({'action':'create VPS'})
    create_plan = router.build_execution_plan(create, {'action':'create VPS'})
    assert create.approval_required is True
    assert create_plan.approval_required is True
    assert create_plan.execution_allowed is False
    delete = router.route_tool_request({'action':'delete server'})
    delete_plan = router.build_execution_plan(delete, {'action':'delete server'})
    assert delete.blocked is True
    assert delete_plan.execution_allowed is False
