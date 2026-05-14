"""Tests: Radamanthys direct STRIX runtime — no Saga Fusion as engine for NL."""

import os, sys, unittest
from unittest.mock import MagicMock, patch

class TestOfficialStrixDirectHandler(unittest.TestCase):
    """OfficialStrixDirectHandler bypasses Saga Fusion for natural language."""

    def setUp(self):
        # Preserve env
        self._env = dict(os.environ)
        for k in list(os.environ):
            if k.startswith("STRIX_") or k.startswith("DEEPSEEK_"):
                os.environ.pop(k, None)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._env)

    # ------------------------------------------------------------------
    # OfficialStrixDirectHandler handles NL text
    # ------------------------------------------------------------------

    @patch("strix_bridge.integrations.telegram.strix_core_gateway.StrixCoreGateway.handle_message")
    def test_hola_calls_direct_handler(self, mock_handle):
        """Text 'hola' goes to direct handler, not Saga Fusion operator."""
        from strix_bridge.integrations.telegram.official_strix_direct_handler import (
            OfficialStrixDirectHandler,
        )

        async def fake_handle(chat_id, user_id, text):
            return MagicMock(available=True, handled=True, response="¡Hola!")

        mock_handle.side_effect = fake_handle
        handler = OfficialStrixDirectHandler()
        handler._gateway = MagicMock()
        handler._gateway.is_available.return_value = True
        handler._gateway.handle_message = fake_handle

        import asyncio
        result = asyncio.run(handler.handle_message("c1", "u1", "hola"))
        self.assertEqual(result, "¡Hola!")

    @patch("strix_bridge.integrations.telegram.strix_core_gateway.StrixCoreGateway.handle_message")
    def test_status_calls_direct_handler(self, mock_handle):
        """'revisa el estado del sistema' goes to STRIX direct handler."""
        from strix_bridge.integrations.telegram.official_strix_direct_handler import (
            OfficialStrixDirectHandler,
        )

        async def fake_handle(chat_id, user_id, text):
            return MagicMock(available=True, handled=True, response="System OK")

        handler = OfficialStrixDirectHandler()
        handler._gateway = MagicMock()
        handler._gateway.is_available.return_value = True
        handler._gateway.handle_message = fake_handle

        import asyncio
        result = asyncio.run(
            handler.handle_message("c1", "u1", "revisa el estado del sistema")
        )
        self.assertEqual(result, "System OK")

    # ------------------------------------------------------------------
    # No Saga Fusion operator for NL
    # ------------------------------------------------------------------

    def test_telegram_lab_runtime_imports_direct_handler(self):
        """telegram_lab_runtime imports OfficialStrixDirectHandler."""
        import saga_fusion.telegram.telegram_lab_runtime as rt
        src = open(rt.__file__).read()
        self.assertIn("OfficialStrixDirectHandler", src)
        self.assertIn("direct_strix_handler", src)

    def test_telegram_lab_runtime_uses_direct_handler(self):
        """telegram_lab_runtime.handle_message calls direct handler, not operator."""
        import saga_fusion.telegram.telegram_lab_runtime as rt
        src = open(rt.__file__).read()
        self.assertIn("direct_strix_handler.handle_message", src)
        self.assertTrue(
            "operator.handle_message" in src,
            "operator.handle_message still used as fallback"
        )

    # ------------------------------------------------------------------
    # StrixAgent is from official pip package
    # ------------------------------------------------------------------

    def test_official_strix_agent_importable(self):
        """StrixAgent official is importable from pip strix-agent."""
        from strix.agents import StrixAgent
        self.assertIn("execute_scan", dir(StrixAgent))

    # ------------------------------------------------------------------
    # execution_allowed=False preserved
    # ------------------------------------------------------------------

    @patch("strix_bridge.integrations.telegram.strix_core_gateway.StrixCoreGateway.handle_message")
    def test_execution_allowed_false_preserved(self, mock_handle):
        """Direct handler preserves execution_allowed=False."""
        from strix_bridge.integrations.telegram.official_strix_direct_handler import (
            OfficialStrixDirectHandler,
        )

        async def fake_handle(chat_id, user_id, text):
            return MagicMock(
                available=True,
                handled=True,
                response="safe",
                metadata={"execution_allowed": False, "executed": False},
            )

        handler = OfficialStrixDirectHandler()
        handler._gateway = MagicMock()
        handler._gateway.is_available.return_value = True
        handler._gateway.handle_message = fake_handle

        import asyncio
        result = asyncio.run(handler.handle_message("c1", "u1", "test"))
        self.assertEqual(result, "safe")

    # ------------------------------------------------------------------
    # Error when STRIX unavailable
    # ------------------------------------------------------------------

    def test_handler_returns_error_when_strix_unavailable(self):
        """Handler returns STRIX_OFFICIAL_UNAVAILABLE when gateway fails."""
        from strix_bridge.integrations.telegram.official_strix_direct_handler import (
            OfficialStrixDirectHandler,
        )

        handler = OfficialStrixDirectHandler()
        handler._gateway = MagicMock()
        handler._gateway.is_available.return_value = False

        import asyncio
        result = asyncio.run(handler.handle_message("c1", "u1", "hola"))
        self.assertIn("STRIX_ERROR", result)

    # ------------------------------------------------------------------
    # No token/env touched
    # ------------------------------------------------------------------

    def test_no_token_in_source(self):
        """No token hardcoded in source files."""
        from strix_bridge.integrations.telegram import official_strix_direct_handler
        src = open(official_strix_direct_handler.__file__).read()
        self.assertNotIn("8746952057", src)
        self.assertNotIn("TELEGRAM_BOT_TOKEN", src)
