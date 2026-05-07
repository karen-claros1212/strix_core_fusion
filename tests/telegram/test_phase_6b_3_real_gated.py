import asyncio
import json
import logging

from saga_fusion.telegram.approval_workflow import ApprovalWorkflow
from saga_fusion.telegram.mock_telegram_adapter import MockTelegramAdapter
from saga_fusion.telegram.mission_operator import TelegramMissionOperator
from saga_fusion.telegram.replay_guard import ReplayGuard
from saga_fusion.telegram.telegram_config import TelegramConfig, load_telegram_config, validate_real_mode_config
from saga_fusion.telegram.telegram_gateway import TelegramGateway
from saga_fusion.telegram.telegram_types import TelegramMessage


def test_load_config_from_environment(monkeypatch):
    monkeypatch.setenv("TELEGRAM_MODE", "real")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123456:" + "secretTOKENvalue")
    monkeypatch.setenv("TELEGRAM_ALLOWED_USER_IDS", "100, 200")
    monkeypatch.setenv("TELEGRAM_POLLING_ENABLED", "true")
    monkeypatch.setenv("TELEGRAM_WEBHOOK_ENABLED", "false")
    monkeypatch.setenv("TELEGRAM_RATE_LIMIT_PER_MINUTE", "7")

    cfg = load_telegram_config()

    assert cfg.mode == "real"
    assert cfg.allowed_user_ids == ["100", "200"]
    assert cfg.polling_enabled is True
    assert cfg.webhook_enabled is False
    assert cfg.rate_limit_per_minute == 7
    assert "secretTOKENvalue" not in repr(cfg)


def test_real_mode_without_token_blocks_startup():
    cfg = TelegramConfig(mode="real", bot_token="", allowed_user_ids=["123"])
    ok, missing = validate_real_mode_config(cfg)

    assert ok is False
    assert "TELEGRAM_BOT_TOKEN" in missing
    assert TelegramGateway(cfg).start().ok is False


def test_real_mode_without_allowed_users_blocks_startup():
    cfg = TelegramConfig(mode="real", bot_token="123456:" + "secretTOKENvalue", allowed_user_ids=[])
    ok, missing = validate_real_mode_config(cfg)

    assert ok is False
    assert "TELEGRAM_ALLOWED_USER_IDS" in missing
    assert TelegramGateway(cfg).start().ok is False


def test_mock_mode_no_token_required():
    cfg = TelegramConfig(mode="mock", bot_token="", allowed_user_ids=[])

    assert cfg.is_ready is True
    assert MockTelegramAdapter(cfg).start().ok is True


def test_token_does_not_appear_in_logs(caplog):
    token = "123456:" + "secretTOKENvalue"
    cfg = TelegramConfig(mode="real", bot_token=token, allowed_user_ids=[])
    gateway = TelegramGateway(cfg)

    with caplog.at_level(logging.WARNING):
        gateway.start()

    assert token not in caplog.text


def test_unauthorized_user_denied():
    cfg = TelegramConfig(mode="real", bot_token="123456:" + "secretTOKENvalue", allowed_user_ids=["123"])
    gateway = TelegramGateway(cfg)
    response = gateway.handle_message(TelegramMessage(message_id=1, user_id=999, chat_id=1, text="/status"))

    assert response.ok is False
    assert "DENIED" in response.text


def test_r4_generates_approval_required_with_action_hash():
    async def run():
        cfg = TelegramConfig(mode="mock", allowed_user_ids=["diego_claros"])
        operator = TelegramMissionOperator(cfg, MockTelegramAdapter(cfg))
        response = json.loads(await operator.handle_message("123", "diego_claros", "/mission create VPS"))
        assert response["status"] == "approval_required"
        assert response["risk_level"] == "R4"
        assert response["approval_id"]
        assert response["action_hash"]
    asyncio.run(run())


def test_r5_blocked():
    async def run():
        cfg = TelegramConfig(mode="mock", allowed_user_ids=["diego_claros"])
        operator = TelegramMissionOperator(cfg, MockTelegramAdapter(cfg))
        response = json.loads(await operator.handle_message("123", "diego_claros", "/mission delete /tmp"))
        assert response["status"] == "blocked"
        assert response["risk_level"] == "R5"
        assert response["result"]["executed"] is False
    asyncio.run(run())


def test_replay_guard_blocks_repeated_approval_hash():
    workflow = ApprovalWorkflow()
    payload = {"mission_id": "m1", "action": "create VPS"}
    approval_id = workflow.create_approval("m1", payload)

    assert workflow.approve(approval_id, action_payload=payload) is True
    assert workflow.approve(approval_id, action_payload=payload) is False


def test_action_hash_mismatch_blocks_approval():
    workflow = ApprovalWorkflow()
    approval_id = workflow.create_approval("m1", {"mission_id": "m1", "action": "create VPS"})

    assert workflow.approve(approval_id, action_payload={"mission_id": "m1", "action": "delete VPS"}) is False


def test_replay_guard_blocks_reused_callback_hash():
    guard = ReplayGuard()
    assert guard.consume_action_hash("hash1") is True
    assert guard.consume_action_hash("hash1") is False


def test_no_real_telegram_call_in_tests():
    calls = []
    cfg = TelegramConfig(mode="mock", bot_token="", allowed_user_ids=[])
    gateway = TelegramGateway(cfg, api_client=lambda method, payload: calls.append((method, payload)))

    assert gateway.send_message("1", "hello") is True
    assert calls == []
