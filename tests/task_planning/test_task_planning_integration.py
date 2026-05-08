import asyncio
import json

from saga_fusion.llm.llm_config import LLMConfig
from saga_fusion.llm.llm_router import LLMRouter
from saga_fusion.telegram.mission_operator import TelegramMissionOperator
from saga_fusion.telegram.mock_telegram_adapter import MockTelegramAdapter
from saga_fusion.telegram.telegram_config import TelegramConfig


def test_llm_router_exposes_declarative_task_plan_without_execution():
    router = LLMRouter(config=LLMConfig(enabled=False))
    result = router.build_task_plan_from_natural_language("Crea un VPS en Hostinger")
    assert result["executed"] is False
    assert result["plan"]["status"] == "approval_required"
    assert result["intent"]["execution_allowed"] is False
    assert result["intent"]["dry_run"] is True


def test_telegram_mock_records_task_plan_for_r4_and_r5_without_execution():
    async def run():
        cfg = TelegramConfig(mode="mock", allowed_user_ids=["diego_claros"])
        operator = TelegramMissionOperator(cfg, MockTelegramAdapter(cfg))
        r4 = json.loads(await operator.handle_message("123", "diego_claros", "Crea un VPS en Hostinger"))
        assert r4["status"] == "approval_required"
        assert r4["result"]["executed"] is False
        r5 = json.loads(await operator.handle_message("123", "diego_claros", "Elimina el servidor y borra backups"))
        assert r5["status"] == "blocked"
        assert r5["result"]["executed"] is False
        events = [record for record in operator.evidence_logger.records if record["event_type"] == "task_plan_intent"]
        assert any(event["blocked"] is False and event["approval_required"] is True for event in events)
        assert any(event["blocked"] is True and event["execution_allowed"] is False for event in events)
        assert all(event["reporting_ready"] is True for event in events)
    asyncio.run(run())
