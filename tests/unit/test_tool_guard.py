import pytest
from unittest.mock import MagicMock
from saga_fusion.tool_guard import SagaToolGuard
from saga_fusion.security_policy import SagaSecurityPolicy
from saga_fusion.audit_logger import SagaAuditLogger

class TestSagaToolGuard:
    @pytest.fixture
    def guard(self):
        policy = SagaSecurityPolicy()
        logger = SagaAuditLogger()
        return SagaToolGuard(policy, logger)

    def test_denied_action_returns_denied_result(self, guard):
        actions = [{"command": "rm -rf /"}]
        allowed, denied = guard.evaluate_actions(actions, None)
        assert len(denied) == 1
        assert denied[0]["status"] == "DENIED"

    def test_denied_action_not_executed(self, guard):
        actions = [{"command": "rm -rf /"}]
        allowed, denied = guard.evaluate_actions(actions, None)
        assert len(allowed) == 0

    def test_allowed_action_executed(self, guard):
        actions = [{"command": "ls"}]
        allowed, denied = guard.evaluate_actions(actions, None)
        assert len(allowed) == 1

    def test_mixed_actions(self, guard):
        actions = [{"command": "ls"}, {"command": "rm -rf /"}]
        allowed, denied = guard.evaluate_actions(actions, None)
        assert len(allowed) == 1
        assert len(denied) == 1
