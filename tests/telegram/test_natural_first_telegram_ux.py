from __future__ import annotations

import asyncio
import json

from saga_fusion.telegram.mission_operator import TelegramMissionOperator
from saga_fusion.telegram.telegram_config import TelegramConfig
from strix.integrations.telegram import StrixTelegramAdapterResult


def _operator():
    config = TelegramConfig(mode="real", bot_token="123456:" + "x" * 35, allowed_user_ids=["8166253211"])
    return TelegramMissionOperator(config, gateway=None)


class FakeGatewayUnavailable:
    unavailable_reason = "strix_gateway_unavailable_for_test"

    def is_available(self):
        return False

    async def handle_message(self, chat_id, user_id, text):  # pragma: no cover - must not be called when unavailable
        raise AssertionError("gateway handle_message should not be called when unavailable")


class FakeGatewayAvailable:
    unavailable_reason = ""

    def __init__(self):
        self.messages = []

    def is_available(self):
        return True

    async def handle_message(self, chat_id, user_id, text):
        self.messages.append(text)
        return StrixTelegramAdapterResult(
            available=True,
            handled=True,
            response=f"STRIX Core handled: {text}",
            reason="handled_by_real_strix_agent",
        )


def _payload_for(text: str, gateway=None):
    operator = _operator()
    operator.strix_agent_adapter = gateway or FakeGatewayUnavailable()
    raw = asyncio.run(operator.handle_message("8166253211", "8166253211", text))
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw}


def test_hola_never_returns_unknown_command_for_free_text():
    payload = _payload_for("hola")

    assert "Unknown command" not in json.dumps(payload)
    assert payload.get("used_command_parser") is False or payload.get("result", {}).get("used_command_parser") is False
    assert payload.get("execution_allowed", payload.get("result", {})).get("execution_allowed", False) is False if isinstance(payload.get("execution_allowed", payload.get("result", {})), dict) else payload.get("execution_allowed") is False


def test_status_natural_language_does_not_require_slash():
    payload = _payload_for("revisa el estado del sistema")

    assert "Unknown command" not in json.dumps(payload)
    result = payload.get("result", payload)
    assert result.get("used_command_parser") is False
    assert result.get("execution_allowed") is False
    assert result.get("executed") is False


def test_natural_ransomware_selects_workflow_without_slash_command():
    payload = _payload_for("analiza posible ransomware")

    assert payload["status"] == "workflow_plan"
    assert payload["workflow_category"] == "ransomware_response"
    assert payload["used_command_parser"] is False
    assert payload["execution_allowed"] is False


def test_natural_malware_triage_selects_workflow_without_slash_command():
    payload = _payload_for("haz triage defensivo de malware")

    assert payload["status"] == "workflow_plan"
    assert payload["workflow_category"] == "malware_triage"
    assert payload["used_command_parser"] is False
    assert payload["execution_allowed"] is False


def test_natural_webshell_selects_workflow_without_slash_command():
    payload = _payload_for("revisa posible webshell")

    assert payload["status"] == "workflow_plan"
    assert payload["workflow_category"] == "webshell_investigation"
    assert payload["used_command_parser"] is False
    assert payload["execution_allowed"] is False


def test_free_text_routes_to_gateway_when_available_and_skips_command_parser():
    gateway = FakeGatewayAvailable()
    payload = _payload_for("cualquier texto libre", gateway=gateway)

    assert gateway.messages == ["cualquier texto libre"]
    assert payload["routed_to"] == "StrixCoreGateway"
    assert payload["used_command_parser"] is False
    assert payload["llm_fallback_used"] is False
    assert payload["execution_allowed"] is False


def test_fallback_to_llm_router_only_when_gateway_unavailable():
    payload = _payload_for("analiza posible ransomware", gateway=FakeGatewayUnavailable())

    assert payload["routed_to"] == "UnifiedSagaAgent"
    assert payload["used_command_parser"] is False
    assert payload["llm_fallback_used"] is True
    assert payload["workflow_category"] == "ransomware_response"


def test_gateway_available_prevents_llm_fallback():
    payload = _payload_for("analiza posible ransomware", gateway=FakeGatewayAvailable())

    assert payload["routed_to"] == "StrixCoreGateway"
    assert payload["llm_fallback_used"] is False
    assert payload["used_command_parser"] is False


def test_r4_natural_language_requires_approval():
    payload = _payload_for("crea un VPS en Hostinger")

    assert payload["status"] == "approval_required"
    assert payload["risk_level"] == "R4"
    assert payload["result"]["execution_allowed"] is False
    assert payload["result"]["executed"] is False


def test_r5_natural_language_is_blocked():
    payload = _payload_for("elimina servidor y borra backups")

    assert payload["status"] == "blocked"
    assert payload["risk_level"] == "R5"
    assert payload["result"]["execution_allowed"] is False
    assert payload["result"]["executed"] is False


def test_status_slash_still_works():
    payload = _payload_for("/status")

    assert payload["status"] == "ok"
    assert "Operational" in payload["message"]


def test_help_promotes_natural_language_not_command_list():
    operator = _operator()
    raw = asyncio.run(operator.handle_message("8166253211", "8166253211", "/help"))

    assert raw == "Escríbeme en lenguaje natural. Ejemplos:\n revisa estado del sistema, analiza posible ransomware,\n audita repo, genera reporte defensivo."
    assert "/malware_triage" not in raw
    assert "/mission" not in raw
