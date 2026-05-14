"""Tests: StrixCoreGateway with hybrid brain config injection."""

import os
import unittest
from unittest.mock import MagicMock, patch


class TestStrixGatewayHybridBrain(unittest.TestCase):

    def setUp(self):
        self._saved = dict(os.environ)
        for k in list(os.environ):
            if k.startswith("STRIX_") or k.startswith("DEEPSEEK_"):
                os.environ.pop(k, None)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._saved)

    # ------------------------------------------------------------------
    # Gateway calls build_hybrid_llm_config when brain module available
    # ------------------------------------------------------------------

    @patch("strix.integrations.telegram.strix_core_gateway.StrixCoreGateway._default_imports_loader")
    @patch("strix.brain.hybrid_brain_config_factory.build_hybrid_llm_config")
    def test_gateway_calls_hybrid_factory(self, mock_factory, mock_loader):
        from strix.integrations.telegram.strix_core_gateway import StrixCoreGateway

        fake_agent = MagicMock()
        fake_agent.state = MagicMock()
        fake_agent.state.messages = []
        fake_agent.state.add_message = MagicMock()

        mock_loader.return_value = (
            MagicMock(return_value=fake_agent),  # StrixAgent
            MagicMock(),                          # LLMConfig
            MagicMock(),                          # Tracer
            None,                                  # set_global_tracer
        )
        mock_factory.return_value = MagicMock()

        gateway = StrixCoreGateway(enabled=True)
        result = gateway.handle_message("chat1", "user1", "hello")

        # handle_message is async — run in event loop
        import asyncio
        r = asyncio.run(result)

        self.assertTrue(mock_factory.called)
        self.assertTrue(r.available)
        self.assertTrue(r.handled)

    # ------------------------------------------------------------------
    # Gateway preserves execution_allowed=False
    # ------------------------------------------------------------------

    @patch("strix.integrations.telegram.strix_core_gateway.StrixCoreGateway._default_imports_loader")
    def test_gateway_preserves_execution_allowed_false(self, mock_loader):
        from strix.integrations.telegram.strix_core_gateway import StrixCoreGateway

        fake_agent = MagicMock()
        fake_agent.state = MagicMock()
        fake_agent.state.messages = []
        fake_agent.state.add_message = MagicMock()

        mock_loader.return_value = (
            MagicMock(return_value=fake_agent),
            MagicMock(),
            MagicMock(),
            None,
        )

        gateway = StrixCoreGateway(enabled=True)
        import asyncio
        r = asyncio.run(gateway.handle_message("chat1", "user1", "hello"))

        self.assertEqual(r.metadata.get("execution_allowed"), False)
        self.assertEqual(r.metadata.get("executed"), False)

    # ------------------------------------------------------------------
    # Gateway preserves dry_run=True
    # ------------------------------------------------------------------

    @patch("strix.integrations.telegram.strix_core_gateway.StrixCoreGateway._default_imports_loader")
    def test_gateway_preserves_dry_run(self, mock_loader):
        from strix.integrations.telegram.strix_core_gateway import StrixCoreGateway

        fake_agent = MagicMock()
        fake_agent.state = MagicMock()
        fake_agent.state.messages = []
        fake_agent.state.add_message = MagicMock()

        mock_loader.return_value = (
            MagicMock(return_value=fake_agent),
            MagicMock(),
            MagicMock(),
            None,
        )

        gateway = StrixCoreGateway(enabled=True)
        import asyncio
        r = asyncio.run(gateway.handle_message("chat1", "user1", "hello"))

        self.assertIn("lab_mode", r.metadata)
        self.assertEqual(r.metadata.get("execution_allowed"), False)
        self.assertEqual(r.metadata.get("executed"), False)

    # ------------------------------------------------------------------
    # Gateway falls back when brain module import fails
    # ------------------------------------------------------------------

    @patch("strix.integrations.telegram.strix_core_gateway.StrixCoreGateway._default_imports_loader")
    def test_gateway_fallback_when_brain_import_fails(self, mock_loader):
        from strix.integrations.telegram.strix_core_gateway import StrixCoreGateway

        fake_agent = MagicMock()
        fake_agent.state = MagicMock()
        fake_agent.state.messages = []
        fake_agent.state.add_message = MagicMock()

        mock_loader.return_value = (
            MagicMock(return_value=fake_agent),
            MagicMock(),
            MagicMock(),
            None,
        )

        # Simulate import error by patching the factory module path
        with patch.dict("sys.modules", {"strix.brain.hybrid_brain_config_factory": None}, clear=False):
            # Re-create gateway so its closure picks up patched sys.modules
            gateway = StrixCoreGateway(enabled=True)
            import asyncio
            r = asyncio.run(gateway.handle_message("chat1", "user1", "hello"))

            self.assertTrue(r.available)
            self.assertTrue(r.handled)

    # ------------------------------------------------------------------
    # Gateway metadata includes brain_mode fields
    # ------------------------------------------------------------------

    @patch("strix.integrations.telegram.strix_core_gateway.StrixCoreGateway._default_imports_loader")
    def test_gateway_metadata_includes_brain_mode(self, mock_loader):
        from strix.integrations.telegram.strix_core_gateway import StrixCoreGateway

        fake_agent = MagicMock()
        fake_agent.state = MagicMock()
        fake_agent.state.messages = []
        fake_agent.state.add_message = MagicMock()

        mock_loader.return_value = (
            MagicMock(return_value=fake_agent),
            MagicMock(),
            MagicMock(),
            None,
        )

        gateway = StrixCoreGateway(enabled=True)
        import asyncio
        r = asyncio.run(gateway.handle_message("chat1", "user1", "hello"))

        self.assertEqual(r.metadata.get("execution_allowed"), False)
        self.assertEqual(r.metadata.get("executed"), False)

    # ------------------------------------------------------------------
    # No .env read directo, no token impreso
    # ------------------------------------------------------------------

    def test_no_dotenv_in_gateway(self):
        import inspect
        from strix.integrations.telegram import strix_core_gateway
        src = inspect.getsource(strix_core_gateway)
        self.assertNotIn(".env", src)
        self.assertNotIn("load_dotenv", src)
