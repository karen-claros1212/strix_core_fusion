import pytest

from saga_fusion.skills import SkillManifest, SkillRegistry


def make_manifest(**overrides):
    data = dict(
        name="repo_audit_skill",
        version="1.0.0",
        description="Repository audit metadata",
        category="repo_audit",
        permissions=("read_repo_metadata",),
        allowed_tools=("repo_audit",),
        required_env=(),
        risk_level="R3",
        entrypoint="saga_fusion.skills.repo_audit:describe",
        enabled=True,
        metadata={},
    )
    data.update(overrides)
    return SkillManifest(**data)


def test_register_get_enable_disable_and_list_enabled():
    registry = SkillRegistry()
    manifest = registry.register(make_manifest(enabled=False))
    assert registry.get("REPO_AUDIT_SKILL") == manifest
    assert registry.list_enabled() == []
    enabled = registry.enable("repo_audit_skill")
    assert enabled.enabled is True
    assert registry.list_enabled() == [enabled]
    disabled = registry.disable("repo_audit_skill")
    assert disabled.enabled is False


def test_duplicate_rejected():
    registry = SkillRegistry()
    registry.register(make_manifest())
    with pytest.raises(ValueError, match="duplicate"):
        registry.register(make_manifest())


def test_invalid_manifest_rejected():
    registry = SkillRegistry()
    with pytest.raises(ValueError, match="dangerous permission"):
        registry.register(make_manifest(name="bad", permissions=("shell",)))
