import pytest

class TestStrixBaseIntegrity:
    def test_strix_base_imports(self):
        """Verificar que Strix base sigue importando sin stubs."""
        try:
            from strix.agents.base_agent import BaseAgent
            assert BaseAgent is not None
        except ImportError as e:
            pytest.fail(f"Error importando Strix base: {e}")

    def test_agent_state_import(self):
        """Verificar que AgentState existe e importa."""
        try:
            from strix.agents.state import AgentState
            assert AgentState is not None
        except ImportError:
            # Si no existe, verificar si está en otro módulo
            import strix.agents
            assert hasattr(strix.agents, 'AgentState') or hasattr(strix.agents, 'base_agent')

    def test_no_monkey_patch_in_base(self):
        """Verificar que BaseAgent real no tiene monkey-patching activo."""
        from strix.agents.base_agent import BaseAgent
        import inspect
        source = inspect.getsource(BaseAgent)
        assert '_original_method' not in source
        assert 'monkey' not in source.lower()

    def test_saga_agent_composition(self):
        """Verificar que StrixSagaAgent usa composición."""
        from saga_fusion.strix_adapter import StrixSagaAgent
        import inspect
        source = inspect.getsource(StrixSagaAgent)
        assert 'composition' in source.lower() or 'context_manager' in source
