import pytest
from saga_fusion.tool_scoping import ToolScope, ToolsetScopeRegistry


def test_default_toolsets_declared_by_required_categories():
    registry = ToolsetScopeRegistry()
    names = {scope.name for scope in registry.list_toolsets()}
    assert {"repo_audit", "secret_audit", "docker_audit", "reporting", "cloudops_plan", "llm_only"}.issubset(names)
    assert "repo_audit" in registry.allowed_tools_for("repo_audit")
    assert "cloudops_plan" in registry.denied_tools_for("repo_audit")


def test_register_custom_toolset_and_reject_overlap():
    registry = ToolsetScopeRegistry()
    scope = registry.register(ToolScope("custom", "reporting", ("status",), ("cloudops_plan",)))
    assert registry.get("custom") == scope
    with pytest.raises(ValueError, match="both allow and deny"):
        registry.register(ToolScope("bad", "repo_audit", ("status",), ("status",)))
