from saga_fusion.defensive_workflows import run_credential_theft_workflow


def test_credential_theft_redacts_and_never_exposes_secrets():
    plan = run_credential_theft_workflow(summary="token=dummyredactionvalue suspected", affected_identity="user@example.com")
    payload = plan.to_dict()
    text = str(payload)
    assert plan.execution_allowed is False
    assert plan.evidence_required and plan.report_required
    assert payload["evidence"]["secret_display"] is False
    assert payload["evidence"]["exfiltration"] is False
    assert "dummyredactionvalue" not in text
    assert "[REDACTED]" in text
