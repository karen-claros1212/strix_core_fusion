from __future__ import annotations

import asyncio
import json

from saga_fusion.telegram.lab_mode import assert_lab_mode
from saga_fusion.telegram.telegram_config import TelegramConfig
from saga_fusion.telegram.telegram_lab_runtime import TelegramLabRuntime, build_arg_parser


class FakeTelegramApi:
    def __init__(self, updates=None, get_me_ok=True):
        self.updates = list(updates or [])
        self.get_me_ok = get_me_ok
        self.calls = []

    def request(self, method, payload=None):
        self.calls.append((method, payload or {}))
        if method == "getMe":
            if not self.get_me_ok:
                return {"ok": False, "description": "unauthorized"}
            return {"ok": True, "result": {"username": "RadamanthysCyberBot"}}
        if method == "getUpdates":
            batch = self.updates
            self.updates = []
            return {"ok": True, "result": batch}
        if method == "sendMessage":
            return {"ok": True, "result": {"message_id": 99}}
        return {"ok": False, "description": "unknown_method"}


def _message(update_id: int, text: str, user_id: int = 8166253211, chat_id: int = 8166253211):
    return {
        "update_id": update_id,
        "message": {
            "message_id": update_id,
            "from": {"id": user_id, "is_bot": False},
            "chat": {"id": chat_id, "type": "private"},
            "text": text,
        },
    }


def test_preflight_blocks_without_real_mode_or_token():
    config = TelegramConfig(mode="mock", bot_token="", allowed_user_ids=["8166253211"])
    runtime = TelegramLabRuntime(config=config, api=FakeTelegramApi())

    preflight = runtime.preflight()

    assert preflight.ok is False
    assert "real" in preflight.reason
    assert preflight.to_redacted_dict()["token"] == ""


def test_preflight_uses_get_me_and_redacts_token_marker():
    config = TelegramConfig(mode="real", bot_token="123456:" + "x" * 35, allowed_user_ids=["8166253211"])
    fake = FakeTelegramApi()
    runtime = TelegramLabRuntime(config=config, api=fake)

    preflight = runtime.preflight()
    payload = preflight.to_redacted_dict()

    assert preflight.ok is True
    assert preflight.bot_username == "RadamanthysCyberBot"
    assert payload["token"] == "[REDACTED]"
    assert fake.calls[0][0] == "getMe"
    assert config.bot_token not in json.dumps(payload)


def test_lab_runtime_routes_natural_language_to_strix_main_engine_phishing_report_pack_without_real_calls():
    config = TelegramConfig(mode="real", bot_token="123456:" + "x" * 35, allowed_user_ids=["8166253211"])
    fake = FakeTelegramApi(updates=[_message(1, "analiza si esto parece phishing")])
    runtime = TelegramLabRuntime(config=config, api=fake)

    result = asyncio.run(runtime.run(max_messages=1, max_seconds=5, poll_timeout_seconds=1))

    assert result["status"] == "ok"
    assert result["messages_handled"] == 1
    send_payload = next(payload for method, payload in fake.calls if method == "sendMessage")
    response = json.loads(send_payload["text"])
    assert response["routed_by"] == "strix_main_engine"
    assert response["strix_main_engine_primary"] is True
    assert response["saga_control_layer"] is True
    assert response["workflow_category"] == "phishing_attachment"
    assert response["pack_id"].startswith("defensive-pack-")
    assert response["evidence_refs"] and response["report_refs"] and response["manifest_refs"]
    assert response["execution_allowed"] is False
    assert response["executed"] is False
    assert response["non_authoritative"] is True
    assert response["evidence_required"] is True
    assert response["report_required"] is True
    assert assert_lab_mode(response) is True
    assert result["evidence"][0]["real_telegram_transport"] is True
    assert result["evidence"][0]["execution_allowed"] is False
    assert config.bot_token not in json.dumps(result)


def test_lab_runtime_natural_status_message_uses_strix_main_engine_not_defensive_router():
    config = TelegramConfig(mode="real", bot_token="123456:" + "x" * 35, allowed_user_ids=["8166253211"])
    fake = FakeTelegramApi(updates=[_message(2, "revisa el estado del sistema")])
    runtime = TelegramLabRuntime(config=config, api=fake)

    result = asyncio.run(runtime.run(max_messages=1, max_seconds=5, poll_timeout_seconds=1))

    assert result["status"] == "ok"
    send_payload = next(payload for method, payload in fake.calls if method == "sendMessage")
    response = json.loads(send_payload["text"])
    assert response["result"]["routed_by"] == "strix_main_engine"
    assert response["result"]["strix_main_engine_primary"] is True
    assert response["result"]["saga_control_layer"] is True
    assert response["result"]["execution_allowed"] is False
    assert response["result"]["executed"] is False
    assert response["result"]["non_authoritative"] is True


def test_lab_runtime_acknowledges_handled_updates_before_bounded_exit():
    config = TelegramConfig(mode="real", bot_token="123456:" + "x" * 35, allowed_user_ids=["8166253211"])
    fake = FakeTelegramApi(updates=[_message(10, "estado defensa")])
    runtime = TelegramLabRuntime(config=config, api=fake)

    result = asyncio.run(runtime.run(max_messages=1, max_seconds=5, poll_timeout_seconds=1))

    ack_payloads = [
        payload
        for method, payload in fake.calls
        if method == "getUpdates" and payload.get("offset") == 11 and payload.get("timeout") == 0
    ]
    assert result["status"] == "ok"
    assert ack_payloads
    assert result["evidence"][-1] == {"event": "telegram_lab_ack", "offset": 11, "ack_ok": True}


def test_service_mode_parser_does_not_require_bounded_limits():
    args = build_arg_parser().parse_args(["--service", "--poll-timeout-seconds", "1"])

    assert args.service is True
    assert args.max_messages == 2
    assert args.max_seconds == 120
    assert args.poll_timeout_seconds == 1


def test_lab_runtime_service_mode_polls_and_acknowledges_without_bounded_window():
    config = TelegramConfig(mode="real", bot_token="123456:" + "x" * 35, allowed_user_ids=["8166253211"])
    fake = FakeTelegramApi(updates=[_message(20, "/defense_status")])
    runtime = TelegramLabRuntime(config=config, api=fake)

    result = asyncio.run(runtime.run_service(max_polls=2, poll_timeout_seconds=1, idle_sleep_seconds=0))

    assert result["status"] == "ok"
    assert result["service_mode"] is True
    assert result["polls"] == 2
    assert result["messages_handled"] == 1
    send_payload = next(payload for method, payload in fake.calls if method == "sendMessage")
    response = json.loads(send_payload["text"])
    assert response["routed_by"] == "defensive_command_router_fallback"
    assert response["workflow_category"] == "defense_status"
    assert response["execution_allowed"] is False
    assert response["executed"] is False
    assert response["non_authoritative"] is True
    assert response["evidence_required"] is True
    assert response["report_required"] is True
    assert any(item["event"] == "telegram_lab_service_started" for item in result["evidence"])
    ack_payloads = [
        payload
        for method, payload in fake.calls
        if method == "getUpdates" and payload.get("offset") == 21 and payload.get("timeout") == 0
    ]
    assert ack_payloads
    assert config.bot_token not in json.dumps(result)



def test_lab_runtime_free_text_capabilities_goes_to_strix_main_engine():
    config = TelegramConfig(mode="real", bot_token="123456:" + "x" * 35, allowed_user_ids=["8166253211"])
    fake = FakeTelegramApi(updates=[_message(30, "que puedes hacer")])
    runtime = TelegramLabRuntime(config=config, api=fake)

    result = asyncio.run(runtime.run(max_messages=1, max_seconds=5, poll_timeout_seconds=1))

    assert result["status"] == "ok"
    send_payload = next(payload for method, payload in fake.calls if method == "sendMessage")
    response = json.loads(send_payload["text"])
    assert response["routed_by"] == "strix_main_engine"
    assert response["strix_main_engine_primary"] is True
    assert response["saga_control_layer"] is True
    assert response["execution_allowed"] is False
    assert "analiza si esto parece phishing" in response["examples"]


def test_lab_runtime_free_text_suspicious_process_goes_to_strix_main_engine_report_pack():
    config = TelegramConfig(mode="real", bot_token="123456:" + "x" * 35, allowed_user_ids=["8166253211"])
    fake = FakeTelegramApi(updates=[_message(31, "quiero revisar procesos raros")])
    runtime = TelegramLabRuntime(config=config, api=fake)

    result = asyncio.run(runtime.run(max_messages=1, max_seconds=5, poll_timeout_seconds=1))

    assert result["status"] == "ok"
    send_payload = next(payload for method, payload in fake.calls if method == "sendMessage")
    response = json.loads(send_payload["text"])
    assert response["routed_by"] == "strix_main_engine"
    assert response["workflow_category"] == "suspicious_process"
    assert response["pack_id"].startswith("defensive-pack-")
    assert response["execution_allowed"] is False
    assert response["executed"] is False
    assert response["evidence_refs"] and response["report_refs"] and response["manifest_refs"]


def test_lab_runtime_defensive_router_is_only_fallback_when_main_engine_unavailable():
    config = TelegramConfig(mode="real", bot_token="123456:" + "x" * 35, allowed_user_ids=["8166253211"])
    fake = FakeTelegramApi(updates=[_message(32, "estado defensa")])
    runtime = TelegramLabRuntime(config=config, api=fake)
    runtime.operator.main_engine_available = False

    result = asyncio.run(runtime.run(max_messages=1, max_seconds=5, poll_timeout_seconds=1))

    assert result["status"] == "ok"
    send_payload = next(payload for method, payload in fake.calls if method == "sendMessage")
    response = json.loads(send_payload["text"])
    assert response["routed_by"] == "defensive_command_router_fallback"
    assert response["strix_main_engine_primary"] is False
    assert response["workflow_category"] == "defense_status"
    assert response["execution_allowed"] is False
