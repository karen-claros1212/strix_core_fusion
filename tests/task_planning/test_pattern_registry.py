from saga_fusion.task_planning import PatternRegistry, TaskRisk


def test_registry_has_default_clean_room_patterns():
    registry = PatternRegistry()
    ids = {pattern.pattern_id for pattern in registry.list_patterns()}
    assert "repo_audit_dry_run" in ids
    assert "cloud_create_approval" in ids
    assert "destructive_block" in ids
    assert registry.get("repo_audit_dry_run").tool_name == "repo_audit"


def test_registry_highest_risk_match_wins():
    registry = PatternRegistry()
    pattern = registry.match("please create VPS then delete backups")
    assert pattern.pattern_id == "destructive_block"
    assert pattern.risk_level == TaskRisk.R5
