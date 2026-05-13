from saga_fusion.telegram.lab_mode import apply_lab_mode, assert_lab_mode, DEFAULT_LAB_MODE


def test_apply_lab_mode_enforces_non_executing_contract():
    payload = apply_lab_mode({"execution_allowed": True, "executed": True, "token": "dummy-secret"})
    assert payload["lab_mode"] is True
    assert payload["execution_allowed"] is False
    assert payload["executed"] is False
    assert payload["evidence_required"] is True
    assert payload["report_required"] is True
    assert payload["non_authoritative"] is True
    assert payload["token"] == "[REDACTED]"
    assert assert_lab_mode(payload) is True


def test_default_lab_mode_blocks_real_world_actions():
    flags = DEFAULT_LAB_MODE.to_dict()
    assert flags["real_telegram_used"] is False
    assert flags["malware_executed"] is False
    assert flags["attachment_executed"] is False
    assert flags["offensive_payload_created"] is False
    assert flags["webshell_generated"] is False
    assert flags["cloudops_used"] is False
