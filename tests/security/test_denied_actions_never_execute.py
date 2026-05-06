import pytest
from unittest.mock import MagicMock, call
from saga_fusion.strix_adapter import StrixSagaAgent

class TestDeniedActionsNeverExecute:
    def setup_method(self):
        self.mock_llm = MagicMock()
        self.mock_executor = MagicMock()
        self.agent = StrixSagaAgent(
            llm=self.mock_llm,
            executor=self.mock_executor
        )

    def test_denied_action_not_in_executor_calls(self):
        # Simulate an action that will be denied
        self.agent._current_actions = [{"command": "rm -rf /"}]
        
        # Execute
        self.agent._execute_actions(self.agent._current_actions)
        
        # Check that executor was NOT called
        self.mock_executor.execute.assert_not_called()

    def test_no_echo_replacement(self):
        # Ensure no dangerous command is replaced by echo
        actions = [{"command": "rm -rf /"}]
        allowed, denied = self.agent.tool_guard.evaluate_actions(actions, self.mock_executor)
        
        denied_cmd = denied[0]['action'].get('command', '')
        assert 'echo' not in denied_cmd.lower() or 'denied' in denied_cmd.lower()
