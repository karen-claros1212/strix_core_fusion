from saga_fusion.memory import ContextItem, MemoryPolicy, MemoryRecord, MemoryScope, MemorySensitivity


def test_memory_policy_secret_blocked_and_untrusted_non_authoritative():
    policy = MemoryPolicy()
    blocked = policy.can_include(ContextItem("secret", sensitivity=MemorySensitivity.SECRET_BLOCKED))
    assert blocked.allowed is False
    decision = policy.can_include(ContextItem("user approved preference", scope=MemoryScope.USER_APPROVED, user_approved=True))
    assert decision.allowed is True
    assert decision.authoritative is False
    assert decision.untrusted is True


def test_memory_policy_cannot_downgrade_r4_r5():
    policy = MemoryPolicy()
    assert policy.effective_risk("R4", "R1") == "R4"
    assert policy.effective_risk("R5", "R0") == "R5"
    assert policy.effective_risk("R2", "R4") == "R4"
    assert "PromptSecurity" in policy.non_authoritative_banner()
    assert "MissionPolicy" in policy.non_authoritative_banner()
