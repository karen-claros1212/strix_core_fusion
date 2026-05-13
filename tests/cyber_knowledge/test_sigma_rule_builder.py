import pytest

from saga_fusion.cyber_knowledge import SafetyValidationError, SigmaRuleBuilder


def test_sigma_builder_emits_defensive_yaml():
    rule = SigmaRuleBuilder().build_rule(
        "Suspicious Process Metadata",
        {"product": "windows", "category": "process_creation"},
        {"selection": {"Image|endswith": ["\\suspicious.exe"], "CommandLine|contains": "--checkin"}},
        tags=("attack.command_and_control", "defensive"),
    )
    assert rule.execution_allowed is False
    assert "x_strix_safety:" in rule.content
    assert "execution_allowed: false" in rule.content
    assert "condition: selection" in rule.content


def test_sigma_builder_rejects_offensive_bypass_request():
    with pytest.raises(SafetyValidationError):
        SigmaRuleBuilder().build_rule(
            "EDR bypass helper",
            {"product": "windows"},
            {"selection": {"CommandLine|contains": "disable defender edr bypass"}},
        )
