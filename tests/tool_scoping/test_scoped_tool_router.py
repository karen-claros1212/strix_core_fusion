from saga_fusion.skills import SkillPolicy, SkillRegistry
from saga_fusion.tool_routing import ToolRouter
from saga_fusion.tool_scoping import ScopedToolRouter, ToolLoopGuard


def test_scoped_router_allows_in_scope_and_preserves_no_execution():
    router = ScopedToolRouter(loop_guard=ToolLoopGuard(max_tool_calls=5, max_repeated_tool_calls=3))
    decision = router.route_tool_request(
        {"tool_name": "repo_audit", "action": "repo audit dry-run"},
        context={"mission_id": "m1", "mission_allowed_tools": ["repo_audit"]},
    )
    plan = router.build_execution_plan(decision, {"tool_name": "repo_audit", "action": "repo audit dry-run"})
    assert decision.allowed is True
    assert decision.reason == "allowed_by_tool_route_policy"
    assert plan.dry_run is True
    assert plan.execution_allowed is False
    assert router.executed is False
    assert router.tool_router.executed is False


def test_scoped_router_blocks_unknown_out_of_scope_loop_and_recursion():
    router = ScopedToolRouter(loop_guard=ToolLoopGuard(max_tool_calls=10, max_repeated_tool_calls=1))
    unknown = router.route_tool_request({"tool_name": "hermes_execute", "action": "run"}, context={"allowed_tools": ["hermes_execute"]})
    out = router.route_tool_request({"tool_name": "status", "action": "status"}, context={"allowed_tools": ["repo_audit"]})
    assert unknown.reason == "unknown_tool_blocked"
    assert out.reason == "out_of_scope_tool_blocked"
    ctx = {"mission_id": "m2", "allowed_tools": ["repo_audit"]}
    assert router.route_tool_request({"tool_name": "repo_audit", "action": "audit", "target": "."}, context=ctx).allowed is True
    loop = router.route_tool_request({"tool_name": "repo_audit", "action": "audit", "target": "."}, context=ctx)
    assert loop.blocked is True
    assert loop.reason == "repeated_tool_call_loop_blocked"
    recursive = router.route_tool_request(
        {"tool_name": "repo_audit", "action": "audit", "target": "."},
        context={"mission_id": "m3", "allowed_tools": ["repo_audit"], "active_tool_stack": ["repo_audit"]},
    )
    assert recursive.blocked is True
    assert recursive.reason == "recursive_tool_call_blocked"


def test_existing_tool_router_and_skill_policy_still_intact():
    base = ToolRouter()
    base_decision = base.route_tool_request({"action": "repo audit dry-run", "target": "repo"})
    assert base_decision.allowed is True
    assert base.executed is False
    skill_decision = SkillPolicy(SkillRegistry()).decide("missing")
    assert skill_decision.blocked is True
    assert skill_decision.reason == "unknown_skill_blocked"
