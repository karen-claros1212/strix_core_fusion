from saga_fusion.tool_scoping import ToolLoopGuard


def test_repeated_tool_loop_blocked():
    guard = ToolLoopGuard(max_tool_calls=10, max_repeated_tool_calls=2)
    context = {"mission_id": "loop"}
    assert guard.check("repo_audit", {"target": "."}, context) is None
    assert guard.check("repo_audit", {"target": "."}, context) is None
    decision = guard.check("repo_audit", {"target": "."}, context)
    assert decision.blocked is True
    assert decision.reason == "repeated_tool_call_loop_blocked"
    assert decision.evidence_metadata["repeated_tool_calls"] == 3


def test_max_tool_calls_blocked_per_mission():
    guard = ToolLoopGuard(max_tool_calls=2, max_repeated_tool_calls=5)
    assert guard.check("repo_audit", {"n": 1}, {"mission_id": "m"}) is None
    assert guard.check("secret_scan", {"n": 2}, {"mission_id": "m"}) is None
    decision = guard.check("docker_audit", {"n": 3}, {"mission_id": "m"})
    assert decision.blocked is True
    assert decision.reason == "max_tool_calls_exceeded"


def test_recursion_blocked():
    guard = ToolLoopGuard()
    decision = guard.check("repo_audit", {"target": "."}, {"mission_id": "m", "active_tool_stack": ["status", "repo_audit"]})
    assert decision.blocked is True
    assert decision.reason == "recursive_tool_call_blocked"
    assert "repo_audit" in decision.evidence_metadata["active_stack"]
