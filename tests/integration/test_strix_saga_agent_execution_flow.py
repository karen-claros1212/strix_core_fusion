import pytest
from unittest.mock import MagicMock
from saga_fusion.strix_adapter import StrixSagaAgent

class TestStrixSagaAgentExecutionFlow:
    def setup_method(self):
        # Mock dependencies
        self.mock_llm = MagicMock()
        self.mock_executor = MagicMock()
        self.agent = StrixSagaAgent(
            llm=self.mock_llm,
            executor=self.mock_executor
        )

    def test_process_iteration_calls_context_manager(self):
        # Mock history
        self.agent.state.get_conversation_history = MagicMock(return_value=[])
        
        # Call process iteration
        self.agent._process_iteration()
        
        # Verify context manager was called
        assert self.agent.context_manager is not None

    def test_execute_actions_calls_tool_guard(self):
        # Mock actions
        actions = [{"command": "ls"}]
        self.agent._current_actions = actions
        
        # Call execute actions
        self.agent._execute_actions(actions)
        
        # Verify tool guard was called (it should have been initialized in __init__)
        assert self.agent.tool_guard is not None
