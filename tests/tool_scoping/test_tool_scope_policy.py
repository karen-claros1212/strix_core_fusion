from saga_fusion.skills import SkillManifest
from saga_fusion.tool_scoping import ToolScopePolicy


def make_skill(**overrides):
    data = dict(
        name="repo_skill",
        version="1.0.0",
        description="Repo audit metadata skill",
        category="repo_audit",
        permissions=("read_repo_metadata",),
        allowed_tools=("repo_audit",),
        required_env=(),
        risk_level="R3",
        entrypoint="saga_fusion.skills.repo:describe",
        enabled=True,
        metadata={},
    )
    data.update(overrides)
    return SkillManifest(**data)


def test_allowed_tool_in_mission_skill_workflow_scope_passes():
    policy = ToolScopePolicy()
    context = {
        "mission_id": "m1",
        "mission_tool_scopes": {"m1": ["repo_audit", "secret_scan"]},
        "workflow": "repo",
        "workflow_tool_scopes": {"repo": ["repo_audit", "report_generate"]},
        "skill_manifest": make_skill(allowed_tools=("repo_audit", "docker_audit")),
    }
    decision = policy.decide({"tool_name": "repo_audit", "action": "repo audit"}, context=context)
    assert decision.allowed is True
    assert decision.reason == "allowed_by_tool_scope_policy"
    assert decision.evidence_metadata["scope_sources"] == ["mission:m1", "skill", "workflow:repo"]


def test_out_of_scope_tool_blocked():
    decision = ToolScopePolicy().decide(
        {"tool_name": "secret_scan", "action": "secret scan"},
        context={"mission_allowed_tools": ["repo_audit"]},
    )
    assert decision.blocked is True
    assert decision.reason == "out_of_scope_tool_blocked"


def test_unknown_tool_blocked():
    decision = ToolScopePolicy().decide({"tool_name": "hermes_execute", "action": "run"}, context={"allowed_tools": ["hermes_execute"]})
    assert decision.blocked is True
    assert decision.reason == "unknown_tool_blocked"


def test_r4_tool_requires_approval_even_when_in_scope():
    decision = ToolScopePolicy().decide(
        {"tool_name": "cloudops_plan", "action": "create VPS"},
        context={"toolset": "cloudops_plan"},
    )
    assert decision.approval_required is True
    assert decision.reason == "risk_r4_requires_approval"


def test_r5_tool_blocked_even_when_in_scope():
    decision = ToolScopePolicy().decide(
        {"tool_name": "cloudops_plan", "action": "delete server and wipe backups"},
        context={"toolset": "cloudops_plan"},
    )
    assert decision.blocked is True
    assert decision.reason == "risk_r5_blocked"


def test_skill_cannot_widen_own_scope():
    decision = ToolScopePolicy().decide(
        {"tool_name": "repo_audit", "action": "repo audit"},
        context={"skill_manifest": make_skill(allowed_tools=("repo_audit",)), "skill_requested_allowed_tools": ["repo_audit", "cloudops_plan"]},
    )
    assert decision.blocked is True
    assert decision.reason == "skill_cannot_widen_own_scope"
