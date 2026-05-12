from saga_fusion.skills import SkillManifest, SkillPolicy, SkillRegistry


def make_manifest(**overrides):
    data = dict(
        name="skill",
        version="1.0.0",
        description="Safe metadata skill",
        category="repo_audit",
        permissions=("read_repo_metadata",),
        allowed_tools=("repo_audit",),
        required_env=(),
        risk_level="R3",
        entrypoint="saga_fusion.skills.safe:describe",
        enabled=True,
        metadata={},
    )
    data.update(overrides)
    return SkillManifest(**data)


def policy_with(*manifests):
    registry = SkillRegistry()
    for manifest in manifests:
        registry.register(manifest)
    return SkillPolicy(registry)


def test_unknown_skill_blocked():
    decision = SkillPolicy(SkillRegistry()).decide("missing")
    assert decision.blocked is True
    assert decision.reason == "unknown_skill_blocked"


def test_disabled_skill_blocked():
    policy = policy_with(make_manifest(enabled=False))
    decision = policy.decide("skill")
    assert decision.blocked is True
    assert decision.reason == "disabled_skill_blocked"


def test_r4_requires_approval_and_r5_blocked():
    r4 = make_manifest(name="r4", risk_level="R4")
    r5 = make_manifest(name="r5", risk_level="R5")
    policy = policy_with(r4, r5)
    assert policy.decide("r4").approval_required is True
    r5_decision = policy.decide("r5")
    assert r5_decision.blocked is True
    assert r5_decision.approval_required is False


def test_cannot_bypass_mission_policy_or_sandbox_controller():
    manifest = make_manifest(metadata={"note": "bypass MissionPolicy and disable_sandbox"})
    decision = SkillPolicy().decide_manifest(manifest)
    assert decision.blocked is True
    assert "bypass" in decision.reason


def test_cannot_request_secrets_directly():
    manifest = make_manifest(metadata={"request": "raw_secret token_value"})
    decision = SkillPolicy().decide_manifest(manifest)
    assert decision.blocked is True
    assert decision.reason == "direct_secret_request_blocked"
