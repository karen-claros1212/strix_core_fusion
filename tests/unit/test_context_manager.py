import pytest
from saga_fusion.context_manager import SagaContextManager

class TestContextManager:
    def setup_method(self):
        self.cm = SagaContextManager(llm_config=None)

    def test_empty_history(self):
        assert self.cm.collapse_history([]) == []

    def test_no_system_prompt(self):
        history = [{"role": "user", "content": "hola"}]
        result = self.cm.collapse_history(history)
        assert result == history

    def test_preserves_system_prompt(self):
        history = [
            {"role": "system", "content": "Eres un agente"},
            {"role": "user", "content": "hola"}
        ]
        result = self.cm.collapse_history(history)
        assert result[0]["role"] == "system"

    def test_soft_limit_pruning(self):
        # Simulate a large history that exceeds soft limit (85% of 8192)
        large_history = [{"role": "user", "content": "x" * 1000} for _ in range(30)]
        result = self.cm.collapse_history(large_history)
        # Should return a pruned list, not the original
        assert len(result) < len(large_history)

    def test_hard_limit_summary(self):
        # Simulate a very large history
        very_large_history = [{"role": "user", "content": "x" * 1000} for _ in range(35)]
        result = self.cm.collapse_history(very_large_history)
        # Should contain a summary message
        assert any("[MYTHOS_SUMMARY]" in msg.get("content", "") for msg in result)

    def test_collapse_returns_new_list(self):
        history = [{"role": "user", "content": "test"}]
        result = self.cm.collapse_history(history)
        assert result is not history
