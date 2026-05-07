import asyncio
import json

from saga_fusion.telegram.mission_operator import TelegramMissionOperator
from saga_fusion.telegram.mock_telegram_adapter import MockTelegramAdapter
from saga_fusion.telegram.telegram_config import TelegramConfig


class StubRouter:
    def __init__(self):
        self.called = False

    def build_mission_from_natural_language(self, text, context=None):
        self.called = True
        return {
            'action_type': 'scan',
            'target': 'localhost',
            'arguments': 'localhost',
            'source': 'llm',
        }


def test_telegram_mock_still_works_without_llm():
    async def run():
        cfg = TelegramConfig(mode='mock', allowed_user_ids=['diego_claros'])
        operator = TelegramMissionOperator(cfg, MockTelegramAdapter(cfg))
        response = json.loads(await operator.handle_message('123', 'diego_claros', 'status services'))
        assert response['status'] == 'dry_run'
        assert response['risk_level'] == 'R0'
        assert response['result']['executed'] is False
    asyncio.run(run())


def test_natural_language_uses_brain_when_enabled_mocked():
    async def run():
        cfg = TelegramConfig(mode='mock', allowed_user_ids=['diego_claros'])
        operator = TelegramMissionOperator(cfg, MockTelegramAdapter(cfg))
        router = StubRouter()
        operator.llm_router = router
        response = json.loads(await operator.handle_message('123', 'diego_claros', 'please scan localhost'))
        assert router.called is True
        assert response['action_type'] == 'scan'
        assert response['target'] == 'localhost'
        assert response['status'] == 'dry_run'
        assert response['result']['executed'] is False
    asyncio.run(run())
