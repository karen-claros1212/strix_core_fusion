import asyncio
import os
import sys
from unittest.mock import Mock

import pytest

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from saga_fusion.telegram.approval_workflow import ApprovalWorkflow
from saga_fusion.telegram.evidence_logger import EvidenceLogger
from saga_fusion.telegram.mission_operator import TelegramMissionOperator
from saga_fusion.telegram.mission_parser import MissionParser
from saga_fusion.telegram.mission_policy import MissionPolicy
from saga_fusion.telegram.mock_telegram_adapter import MockTelegramAdapter
from saga_fusion.telegram.rate_limiter import RateLimiter
from saga_fusion.telegram.replay_guard import ReplayGuard
from saga_fusion.telegram.telegram_config import TelegramConfig
from saga_fusion.telegram.telegram_security import TelegramSecurity
from saga_fusion.telegram.telegram_types import MissionRequest, RiskLevel


def test_parse_basic_mission():
    parser = MissionParser()
    request = parser.parse("create VPS")
    assert request.action_type == "create"
    assert request.target == "VPS"


def test_reject_empty_mission():
    parser = MissionParser()
    with pytest.raises(ValueError):
        parser.parse("")


def test_r5_blocked_by_default():
    policy = MissionPolicy()
    request = MissionRequest(action_type="delete", arguments="rm -rf /")
    risk = policy.classify_risk(request)
    assert risk == RiskLevel.R5
    assert policy.requires_approval(risk) is True


def test_r4_requires_approval():
    policy = MissionPolicy()
    request = MissionRequest(action_type="create")
    risk = policy.classify_risk(request)
    assert risk == RiskLevel.R4
    assert policy.requires_approval(risk) is True


def test_create_and_approve():
    workflow = ApprovalWorkflow()
    approval_id = workflow.create_approval("mission-1")
    assert workflow.is_approved(approval_id) is False
    workflow.approve(approval_id)
    assert workflow.is_approved(approval_id) is True


def test_duplicate_mission_blocked():
    guard = ReplayGuard()
    guard.mark_executed("mission-1")
    assert guard.is_duplicate("mission-1") is True


def test_rate_limiter_blocks_flood():
    limiter = RateLimiter(max_requests=2, window_seconds=60)
    assert limiter.is_allowed("user-1") is True
    assert limiter.is_allowed("user-1") is True
    assert limiter.is_allowed("user-1") is False


def test_evidence_log_redacts_secrets():
    config = TelegramConfig(bot_token="mock_token", allowed_user_ids=["diego_claros"])
    security = TelegramSecurity(config)
    mock_audit = Mock()
    logger = EvidenceLogger(audit=mock_audit, security=security)
    request = MissionRequest(arguments="api_key=12345")
    log_data = logger.log_mission(request, {"success": True})
    assert "12345" not in log_data['arguments']
    assert "REDACTED" in log_data['arguments']


def test_mock_adapter_sends_message():
    adapter = MockTelegramAdapter()
    result = adapter.send_message("123", "Hello")
    assert result is True
    assert len(adapter.messages) == 1


def test_operator_end_to_end_dry_run():
    async def run_async_test():
        config = TelegramConfig(bot_token="mock_token", allowed_user_ids=["diego_claros"])
        adapter = MockTelegramAdapter(config=config)
        operator = TelegramMissionOperator(config, adapter)

        response = await operator.handle_message("123", "diego_claros", "/status")
        assert "Operational" in response

        response = await operator.handle_message("123", "diego_claros", "/mission create VPS")
        assert "requires approval" in response

    asyncio.run(run_async_test())


if __name__ == "__main__":
    asyncio.run(test_operator_end_to_end_dry_run())
