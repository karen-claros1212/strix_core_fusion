import asyncio
import json

from saga_fusion.telegram.defensive_command_router import DefensiveCommandRouter
from saga_fusion.telegram.lab_mode import assert_lab_mode
from saga_fusion.telegram.mission_operator import TelegramMissionOperator
from saga_fusion.telegram.mock_telegram_adapter import MockTelegramAdapter
from saga_fusion.telegram.mission_policy import MissionPolicy
from saga_fusion.telegram.telegram_config import TelegramConfig
from saga_fusion.telegram.telegram_gateway import TelegramGateway
from saga_fusion.telegram.telegram_types import MissionRequest, RiskLevel, TelegramMessage


def assert_common_safety(result):
    assert result["lab_mode"] is True
    assert result["execution_allowed"] is False
    assert result["executed"] is False
    assert result["report_required"] is True
    assert result["evidence_required"] is True
    assert result["non_authoritative"] is True
    assert result["real_telegram_used"] is False
    assert result["malware_executed"] is False
    assert result["attachment_executed"] is False
    assert result["offensive_payload_created"] is False
    assert result["webshell_generated"] is False
    assert assert_lab_mode(result) is True


def test_required_commands_route_to_correct_workflows():
    router = DefensiveCommandRouter()
    cases = {
        "/malware_triage": "malware_triage",
        "/ransomware_response": "ransomware_response",
        "/phishing_review": "phishing_attachment",
        "/webshell_investigation": "webshell_investigation",
        "/credential_theft_review": "credential_theft",
        "/suspicious_process_review": "suspicious_process",
    }
    for command, workflow in cases.items():
        result = router.route(command)
        assert result["status"] == "workflow_plan"
        assert result["workflow_category"] == workflow
        assert result["report_id"].startswith("defensive-report-")
        assert result["pack_id"].startswith("defensive-pack-")
        assert result["evidence_refs"] and result["report_refs"] and result["manifest_refs"]
        assert "telegram_summary" in result
        assert result["mitre_mappings"]
        assert result["recommendations"]
        assert_common_safety(result)


def test_natural_language_ransomware_and_webshell_select_correct_workflows():
    router = DefensiveCommandRouter()
    ransomware = router.route("analiza posible ransomware")
    webshell = router.route("revisa posible webshell")
    assert ransomware["workflow_category"] == "ransomware_response"
    assert webshell["workflow_category"] == "webshell_investigation"
    assert_common_safety(ransomware)
    assert_common_safety(webshell)


def test_unknown_command_does_not_execute():
    result = DefensiveCommandRouter().route("/definitely_unknown")
    assert result["status"] == "blocked"
    assert result["blocked"] is True
    assert result["execution_allowed"] is False
    assert result["executed"] is False
    assert result["workflow_category"] is None
    assert_common_safety(result)


def test_no_secrets_in_response():
    result = DefensiveCommandRouter().route("/credential_theft_review token=dummy_token_value password=dummy_password_value")
    serialized = json.dumps(result, sort_keys=True)
    assert "dummy_token_value" not in serialized
    assert "dummy_password_value" not in serialized
    assert "[REDACTED]" in serialized


def test_defense_status_lab_mode():
    result = DefensiveCommandRouter().route("/defense_status")
    assert result["status"] == "ok"
    assert result["workflow_category"] == "defense_status"
    assert "malware_triage" in result["available_workflows"]
    assert_common_safety(result)


def test_telegram_mock_intact_and_no_real_calls():
    config = TelegramConfig(mode="mock", allowed_user_ids=["123"])
    calls = []
    gateway = TelegramGateway(config=config, api_client=lambda method, payload: calls.append((method, payload)))
    assert gateway.send_message("1", "hello") is True
    assert calls == []
    response = gateway.handle_message(TelegramMessage(message_id=1, user_id=123, chat_id=1, text="/malware_triage"))
    assert response.ok is False
    assert "Comando no reconocido" in response.text


def test_operator_routes_defensive_workflow_by_natural_language_without_real_telegram():
    async def run():
        config = TelegramConfig(mode="mock", allowed_user_ids=["123"])
        adapter = MockTelegramAdapter(config=config)
        operator = TelegramMissionOperator(config, adapter)
        response = await operator.handle_message("1", "123", "haz triage defensivo de malware")
        payload = json.loads(response)
        assert payload["workflow_category"] == "malware_triage"
        assert payload["execution_allowed"] is False
        assert payload["used_command_parser"] is False
        assert adapter.messages == []
    asyncio.run(run())


def test_r4_r5_intact():
    policy = MissionPolicy()
    assert policy.classify_risk(MissionRequest(action_type="create", target="VPS")) == RiskLevel.R4
    assert policy.classify_risk(MissionRequest(action_type="delete", arguments="rm -rf /")) == RiskLevel.R5
