from __future__ import annotations

import asyncio
import json

from saga_fusion.telegram.lab_mode import assert_lab_mode
from saga_fusion.telegram.telegram_config import TelegramConfig
from saga_fusion.telegram.telegram_lab_runtime import TelegramLabRuntime


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


def test_lab_runtime_routes_real_update_to_phishing_report_pack_without_real_calls():
    config = TelegramConfig(mode="real", bot_token="123456:" + "x" * 35, allowed_user_ids=["8166253211"])
    fake = FakeTelegramApi(updates=[_message(1, "revisa un adjunto sospechoso en modo seguro")])
    runtime = TelegramLabRuntime(config=config, api=fake)

    result = asyncio.run(runtime.run(max_messages=1, max_seconds=5, poll_timeout_seconds=1))

    assert result["status"] == "ok"
    assert result["messages_handled"] == 1
    send_payload = next(payload for method, payload in fake.calls if method == "sendMessage")
    response = json.loads(send_payload["text"])
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


def test_lab_runtime_status_message_returns_defense_capabilities():
    config = TelegramConfig(mode="real", bot_token="123456:" + "x" * 35, allowed_user_ids=["8166253211"])
    fake = FakeTelegramApi(updates=[_message(2, "estado defensa")])
    runtime = TelegramLabRuntime(config=config, api=fake)

    result = asyncio.run(runtime.run(max_messages=1, max_seconds=5, poll_timeout_seconds=1))

    assert result["status"] == "ok"
    send_payload = next(payload for method, payload in fake.calls if method == "sendMessage")
    response = json.loads(send_payload["text"])
    assert response["status"] == "ok"
    assert response["workflow_category"] == "defense_status"
    assert "phishing_attachment" in response["available_workflows"]
    assert response["execution_allowed"] is False
    assert response["executed"] is False
    assert response["non_authoritative"] is True
    assert assert_lab_mode(response) is True

