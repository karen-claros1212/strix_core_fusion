import pytest

from saga_fusion.cyber_knowledge import SafetyValidationError, YaraRuleBuilder


def test_yara_builder_emits_defensive_metadata_rule():
    rule = YaraRuleBuilder().build_rule("Suspicious Stealer", ["browser_passwords.sqlite", "stealer_config_marker"], tags=("defensive", "triage"))
    assert rule.execution_allowed is False
    assert "defensive_only = true" in rule.content
    assert "execution_allowed = false" in rule.content
    assert "$s1" in rule.content
    assert "browser_passwords.sqlite" in rule.content


def test_yara_builder_rejects_payload_request():
    with pytest.raises(SafetyValidationError):
        YaraRuleBuilder().build_rule("payload", ["reverse shell payload"])
