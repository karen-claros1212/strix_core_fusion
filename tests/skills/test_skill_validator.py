import os

import pytest

from saga_fusion.skills import SkillManifest, SkillValidator
from saga_fusion.task_planning import PatternRegistry, TaskPlanner
from saga_fusion.tool_routing import ToolRouter


def make_manifest(**overrides):
    data = dict(
        name="skill",
        version="1.0.0",
        description="Safe metadata skill",
        category="repo_audit",
        permissions=("read_repo_metadata",),
        allowed_tools=("repo_audit",),
        required_env=("STRIX_TEST_REQUIRED",),
        risk_level="R3",
        entrypoint="saga_fusion.skills.safe:describe",
        enabled=True,
        metadata={},
    )
    data.update(overrides)
    return SkillManifest(**data)


def test_validator_accepts_valid_manifest_without_reading_env_values(monkeypatch):
    monkeypatch.setenv("STRIX_TEST_REQUIRED", "super-secret-value")
    manifest = make_manifest()
    SkillValidator().validate(manifest)
    assert manifest.public_env_requirements() == ("STRIX_TEST_REQUIRED",)
    assert "super-secret-value" not in str(manifest.to_dict())
    assert os.environ["STRIX_TEST_REQUIRED"] == "super-secret-value"


def test_dangerous_permission_rejected():
    with pytest.raises(ValueError, match="dangerous permission"):
        SkillValidator().validate(make_manifest(permissions=("read_secret",)))


def test_required_env_rejects_values_and_entrypoint_format():
    with pytest.raises(ValueError, match="required_env"):
        SkillValidator().validate(make_manifest(required_env=("API_KEY=secret",)))
    with pytest.raises(ValueError, match="entrypoint"):
        SkillValidator().validate(make_manifest(name="bad_entry", entrypoint="not-a-module"))


def test_tool_scope_rejects_unknown_tool_and_router_enforces_allowed_tools():
    with pytest.raises(ValueError, match="unknown allowed tool"):
        SkillValidator().validate(make_manifest(allowed_tools=("hermes_execute",)))

    router = ToolRouter()
    manifest = make_manifest(allowed_tools=("repo_audit",))
    allowed = router.route_tool_request({"action": "repo audit dry-run"}, context={"skill_manifest": manifest})
    blocked = router.route_tool_request({"tool_name": "status", "action": "status"}, context={"skill_manifest": manifest})
    assert allowed.allowed is True
    assert blocked.blocked is True
    assert blocked.reason == "skill_allowed_tools_scope_blocked"


def test_pattern_registry_and_task_planner_reference_skill_metadata_without_execution():
    registry = PatternRegistry()
    updated = registry.attach_skill_metadata("repo_audit_dry_run", {"skill": "skill", "allowed_tools": ["repo_audit"]})
    assert updated.skill_metadata["skill"] == "skill"
    plan = TaskPlanner(registry=registry).plan("repo audit dry-run", target=".")
    assert plan.metadata["skill_metadata"]["allowed_tools"] == ["repo_audit"]
    assert plan.execution_allowed is False
