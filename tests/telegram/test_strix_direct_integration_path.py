from __future__ import annotations

import asyncio
import json

from saga_fusion.telegram.mission_operator import TelegramMissionOperator
from saga_fusion.telegram.telegram_config import TelegramConfig
from strix.integrations.telegram import StrixCoreGateway, StrixTelegramAdapter, StrixTelegramRouter


def _operator():
    config = TelegramConfig(mode="real", bot_token="123456:" + "x" * 35, allowed_user_ids=["8166253211"])
    return TelegramMissionOperator(config, gateway=None)


class FakeUnavailableStrixAdapter:
    unavailable_reason = "strix_agent_unavailable:ImportError"

    def is_available(self):
        return False

    async def handle_message(self, chat_id, user_id, text):
        from strix.integrations.telegram import StrixTelegramAdapterResult

        return StrixTelegramAdapterResult(available=False, handled=False, reason="strix_agent_unavailable:ImportError")


def test_canonical_strix_telegram_import_path_exists():
    assert StrixTelegramAdapter is not None
    assert StrixCoreGateway is not None
    assert StrixTelegramRouter is not None


def test_saga_fusion_strix_engine_is_compatibility_wrapper_only():
    from saga_fusion.strix_engine import StrixAgentAdapter, StrixCoreGateway as WrappedGateway

    assert StrixAgentAdapter is StrixTelegramAdapter
    assert WrappedGateway is StrixCoreGateway
    assert StrixAgentAdapter.__module__.startswith("strix.integrations.telegram")


def test_canonical_adapter_unavailable_does_not_require_saga_fusion_as_brain():
    def broken_imports():
        raise ImportError("real STRIX stack not installed")

    adapter = StrixTelegramAdapter(imports_loader=broken_imports)
    result = asyncio.run(adapter.handle_message("chat", "user", "texto libre"))

    assert result.available is False
    assert result.handled is False
    assert "strix_agent_unavailable" in result.reason
    assert result.metadata["execution_allowed"] is False
    assert result.metadata["executed"] is False


def test_r4_still_requires_approval_when_canonical_adapter_unavailable():
    operator = _operator()
    operator.strix_agent_adapter = FakeUnavailableStrixAdapter()

    raw = asyncio.run(operator.handle_message("8166253211", "8166253211", "crea un VPS en modo seguro"))
    payload = json.loads(raw)

    assert payload["status"] == "approval_required"
    assert payload["risk_level"] == "R4"
    assert payload["result"]["execution_allowed"] is False
    assert payload["result"]["executed"] is False
    assert payload["result"]["routed_by"] == "strix_main_engine"


def test_r5_still_blocked_when_canonical_adapter_unavailable():
    operator = _operator()
    operator.strix_agent_adapter = FakeUnavailableStrixAdapter()

    raw = asyncio.run(operator.handle_message("8166253211", "8166253211", "elimina el servidor y borra backups"))
    payload = json.loads(raw)

    assert payload["status"] == "blocked"
    assert payload["risk_level"] == "R5"
    assert payload["result"]["execution_allowed"] is False
    assert payload["result"]["executed"] is False
    assert payload["result"]["reason"] == "risk_r5_blocked"


def test_no_executed_true_without_sandbox_or_approval_for_safe_status_fallback():
    operator = _operator()
    operator.strix_agent_adapter = FakeUnavailableStrixAdapter()

    raw = asyncio.run(operator.handle_message("8166253211", "8166253211", "revisa el estado del sistema"))
    payload = json.loads(raw)

    result = payload.get("result", payload)
    assert result.get("execution_allowed") is False
    assert result.get("executed") is False
