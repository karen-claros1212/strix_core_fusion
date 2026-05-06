import pytest
from saga_fusion.strix_adapter import StrixSagaAgent
from saga_fusion.context_manager import SagaContextManager
from saga_fusion.security_policy import SagaSecurityPolicy
from saga_fusion.tool_guard import SagaToolGuard
from saga_fusion.audit_logger import SagaAuditLogger
from strix.agents.base_agent import BaseAgent
from strix.agents.state import AgentState

class TestImports:
    def test_base_agent_import(self):
        assert BaseAgent is not None

    def test_strix_saga_agent_import(self):
        assert StrixSagaAgent is not None

    def test_context_manager_import(self):
        assert SagaContextManager is not None

    def test_security_policy_import(self):
        assert SagaSecurityPolicy is not None

    def test_tool_guard_import(self):
        assert SagaToolGuard is not None

    def test_audit_logger_import(self):
        assert SagaAuditLogger is not None
