from saga_fusion.tool_routing import ToolCategory, ToolRegistry, ToolRisk, ToolRoutePolicy


def test_policy_unknown_and_r5_blocked():
    policy = ToolRoutePolicy()
    unknown = policy.decide({'tool_name':'unknown','category':ToolCategory.UNKNOWN,'risk_level':ToolRisk.R4})
    assert unknown.blocked is True
    r5 = policy.decide({'tool_name':'cloudops_plan','category':ToolCategory.CLOUDOPS,'risk_level':ToolRisk.R5})
    assert r5.blocked is True


def test_policy_r4_approval_and_readonly_allowed():
    policy = ToolRoutePolicy()
    r4 = policy.decide({'tool_name':'cloudops_plan','category':ToolCategory.CLOUDOPS,'risk_level':ToolRisk.R4})
    assert r4.approval_required is True
    readonly = policy.decide({'tool_name':'status','category':ToolCategory.READ_ONLY,'risk_level':ToolRisk.R0})
    assert readonly.allowed is True
    assert readonly.blocked is False


def test_policy_enforces_sandbox_required_metadata():
    policy = ToolRoutePolicy(ToolRegistry())
    repo = policy.decide({'tool_name':'repo_audit','category':ToolCategory.REPO_AUDIT,'risk_level':ToolRisk.R3})
    assert repo.sandbox_required is True
    assert repo.route == 'sandbox'
