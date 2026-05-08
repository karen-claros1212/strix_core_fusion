import asyncio
import json

from saga_fusion.telegram.mission_operator import TelegramMissionOperator
from saga_fusion.telegram.mock_telegram_adapter import MockTelegramAdapter
from saga_fusion.telegram.telegram_config import TelegramConfig


def test_telegram_r4_creates_structured_approval_and_r5_has_none():
    async def run():
        cfg = TelegramConfig(mode='mock', allowed_user_ids=['diego_claros'])
        operator = TelegramMissionOperator(cfg, MockTelegramAdapter(cfg))
        r4 = json.loads(await operator.handle_message('123', 'diego_claros', 'Crea un VPS en Hostinger'))
        approval_id = r4['approval_id']
        assert r4['status'] == 'approval_required'
        assert approval_id
        stored = operator.approval_store.get(approval_id)
        assert stored is not None
        assert stored.action_hash == r4['action_hash']
        assert stored.evidence_ref
        r5 = json.loads(await operator.handle_message('123', 'diego_claros', 'Elimina el servidor y borra backups'))
        assert r5['status'] == 'blocked'
        assert r5['approval_id'] is None
    asyncio.run(run())


def test_telegram_approve_and_deny_require_valid_ids_and_hashes():
    async def run():
        cfg = TelegramConfig(mode='mock', allowed_user_ids=['diego_claros'])
        operator = TelegramMissionOperator(cfg, MockTelegramAdapter(cfg))
        assert json.loads(await operator.handle_message('123', 'diego_claros', '/approve'))['reason'] == 'approval_id_required'
        assert json.loads(await operator.handle_message('123', 'diego_claros', '/approve invalid'))['reason'] == 'approval_not_found'
        r4 = json.loads(await operator.handle_message('123', 'diego_claros', 'Crea un VPS en Hostinger'))
        approval_id = r4['approval_id']
        bad = json.loads(await operator.handle_message('123', 'diego_claros', f'/approve {approval_id} bad-hash'))
        assert bad['reason'] == 'action_hash_mismatch'
        r4b = json.loads(await operator.handle_message('123', 'diego_claros', 'Crea un VPS en Hostinger'))
        denied = json.loads(await operator.handle_message('123', 'diego_claros', f'/deny {r4b["approval_id"]}'))
        assert denied['status'] == 'denied'
        assert any(record['event_type'] == 'approval_decision' for record in operator.evidence_logger.records)
    asyncio.run(run())
