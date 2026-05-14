import json

from saga_fusion.telegram.mission_operator import TelegramMissionOperator
from saga_fusion.telegram.telegram_config import TelegramConfig
from saga_fusion.telegram.mock_telegram_adapter import MockTelegramAdapter


def build_operator():
    config = TelegramConfig(mode="mock", allowed_user_ids=["diego_claros"])
    adapter = MockTelegramAdapter()
    return TelegramMissionOperator(config, adapter)


async def _handle(operator, text: str):
    return await operator.handle_message("123", "diego_claros", text)


def test_natural_message_executes_dry_run():
    operator = build_operator()
    response = json.loads(__import__("asyncio").run(_handle(operator, "status services")))

    assert response["status"] == "dry_run"
    assert response["risk_level"] == "R0"
    assert response["result"]["mode"] == "DRY_RUN"
    assert response["result"]["executed"] is False
    assert operator.evidence_logger.records[-1]["status"] == "COMPLETED"


def test_r4_mission_returns_approval_required():
    operator = build_operator()
    response = json.loads(__import__("asyncio").run(_handle(operator, "crea un VPS")))

    assert response["status"] == "approval_required"
    assert response["risk_level"] == "R4"
    assert response["approval_id"]
    assert response["result"]["executed"] is False
    assert operator.evidence_logger.records[-1]["status"] == "PENDING"


def test_r5_mission_is_blocked_without_approval():
    operator = build_operator()
    response = json.loads(__import__("asyncio").run(_handle(operator, "elimina /tmp")))

    assert response["status"] == "blocked"
    assert response["risk_level"] == "R5"
    assert response["approval_id"] is None
    assert response["result"]["reason"] == "risk_r5_blocked"
    assert operator.evidence_logger.records[-1]["status"] == "REJECTED"
