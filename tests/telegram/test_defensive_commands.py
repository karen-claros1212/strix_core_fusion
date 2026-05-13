from saga_fusion.telegram.defensive_commands import (
    COMMAND_TO_WORKFLOW,
    known_defensive_commands,
    map_natural_language,
    parse_defensive_command,
)


def test_defensive_command_mapping_includes_required_commands():
    assert COMMAND_TO_WORKFLOW["malware_triage"] == "malware_triage"
    assert COMMAND_TO_WORKFLOW["ransomware_response"] == "ransomware_response"
    assert COMMAND_TO_WORKFLOW["phishing_review"] == "phishing_attachment"
    assert COMMAND_TO_WORKFLOW["webshell_investigation"] == "webshell_investigation"
    assert COMMAND_TO_WORKFLOW["credential_theft_review"] == "credential_theft"
    assert COMMAND_TO_WORKFLOW["suspicious_process_review"] == "suspicious_process"
    assert "/defense_status" in known_defensive_commands()


def test_malware_triage_command_generates_workflow_request():
    request = parse_defensive_command("/malware_triage observa hash sospechoso")
    assert request.workflow_id == "malware_triage"
    assert request.blocked is False


def test_unknown_command_is_blocked_request():
    request = parse_defensive_command("/unknown_defense")
    assert request.blocked is True
    assert request.status == "blocked"
    assert request.reason == "unknown_defensive_command"


def test_natural_language_required_mappings():
    assert map_natural_language("analiza posible ransomware").workflow_id == "ransomware_response"
    assert map_natural_language("revisa un adjunto sospechoso en modo seguro").workflow_id == "phishing_attachment"
    assert map_natural_language("prepara triage de malware").workflow_id == "malware_triage"
    assert map_natural_language("investiga posible robo de credenciales").workflow_id == "credential_theft"
    assert map_natural_language("revisa posible webshell").workflow_id == "webshell_investigation"
    assert map_natural_language("analiza proceso sospechoso").workflow_id == "suspicious_process"
    assert map_natural_language("estado defensa").command == "defense_status"
