from __future__ import annotations

import asyncio
import json

from saga_fusion.strix_engine import StrixAgentAdapter
from saga_fusion.telegram.mission_operator import TelegramMissionOperator
from saga_fusion.telegram.telegram_config import TelegramConfig


class FakeLLMConfig:
    def __init__(self, interactive=False):
        self.interactive = interactive


class FakeTracer:
    def __init__(self, session_id=""):
        self.session_id = session_id


class FakeState:
    def __init__(self):
        self.messages = []
        self.resumed = 0

    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})

    def resume_from_waiting(self):
        self.resumed += 1
        self.messages.append({"role": "assistant", "content": f"resumed:{self.resumed}"})


class FakeStrixAgent:
    instances = []

    def __init__(self, agent_config=None):
        self.agent_config = agent_config or {}
        self.state = FakeState()
        self.scan_configs = []
        FakeStrixAgent.instances.append(self)

    async def execute_scan(self, scan_config):
        self.scan_configs.append(scan_config)
        self.state.messages.append({"role": "assistant", "content": "real STRIX response"})


def _fake_imports():
    return FakeStrixAgent, FakeLLMConfig, FakeTracer, lambda tracer: None


def test_strix_agent_adapter_unavailable_returns_fallback_signal():
    def broken_imports():
        raise ImportError("no strix agent")

    adapter = StrixAgentAdapter(imports_loader=broken_imports)

    result = asyncio.run(adapter.handle_message("chat", "user", "que puedes hacer"))

    assert result.available is False
    assert result.handled is False
    assert "strix_agent_unavailable" in result.reason
    assert result.metadata["execution_allowed"] is False
    assert result.metadata["executed"] is False


def test_strix_agent_adapter_available_starts_lab_scan_and_returns_assistant_response():
    FakeStrixAgent.instances.clear()
    adapter = StrixAgentAdapter(imports_loader=_fake_imports)

    result = asyncio.run(adapter.handle_message("chat-1", "user-1", "texto libre"))

    assert result.available is True
    assert result.handled is True
    assert result.response == "real STRIX response"
    assert result.reason == "handled_by_real_strix_agent"
    assert result.metadata["saga_control_layer"] is True
    assert result.metadata["execution_allowed"] is False
    agent = FakeStrixAgent.instances[-1]
    assert agent.agent_config["llm_config"].interactive is True
    assert agent.agent_config["lab_mode"] is True
    assert agent.agent_config["execution_allowed"] is False
    assert agent.scan_configs[0]["mode"] == "telegram_lab"
    assert agent.scan_configs[0]["execution_allowed"] is False
    assert {m["role"] for m in agent.state.messages} >= {"user", "assistant"}


def test_strix_agent_adapter_subsequent_message_resumes_existing_session():
    FakeStrixAgent.instances.clear()
    adapter = StrixAgentAdapter(imports_loader=_fake_imports)

    first = asyncio.run(adapter.handle_message("chat-2", "user-1", "hola"))
    second = asyncio.run(adapter.handle_message("chat-2", "user-1", "sigue"))

    assert first.response == "real STRIX response"
    assert second.response == "resumed:1"
    assert len(FakeStrixAgent.instances) == 1
    assert FakeStrixAgent.instances[0].state.resumed == 1


class FakeAvailableAdapter:
    def __init__(self):
        self.messages = []

    async def handle_message(self, chat_id, user_id, text):
        self.messages.append((chat_id, user_id, text))
        from saga_fusion.strix_engine import StrixAgentAdapterResult

        return StrixAgentAdapterResult(
            available=True,
            handled=True,
            response="respuesta desde STRIX real",
            reason="handled_by_real_strix_agent",
        )


class FakeUnavailableAdapter:
    async def handle_message(self, chat_id, user_id, text):
        from saga_fusion.strix_engine import StrixAgentAdapterResult

        return StrixAgentAdapterResult(available=False, handled=False, reason="strix_agent_unavailable:ImportError")


def _operator():
    config = TelegramConfig(mode="real", bot_token="123456:" + "x" * 35, allowed_user_ids=["8166253211"])
    return TelegramMissionOperator(config, gateway=None)


def test_telegram_mission_operator_uses_real_strix_agent_adapter_as_primary_for_free_text():
    operator = _operator()
    fake_adapter = FakeAvailableAdapter()
    operator.strix_agent_adapter = fake_adapter

    raw = asyncio.run(operator.handle_message("8166253211", "8166253211", "qué puedes hacer"))
    payload = json.loads(raw)

    assert fake_adapter.messages == [("8166253211", "8166253211", "qué puedes hacer")]
    assert payload["routed_by"] == "real_strix_agent"
    assert payload["strix_main_engine_primary"] is True
    assert payload["saga_control_layer"] is True
    assert payload["message"] == "respuesta desde STRIX real"
    assert payload["execution_allowed"] is False
    assert payload["executed"] is False


def test_telegram_mission_operator_falls_back_to_saga_fusion_when_adapter_unavailable():
    operator = _operator()
    operator.strix_agent_adapter = FakeUnavailableAdapter()

    raw = asyncio.run(operator.handle_message("8166253211", "8166253211", "analiza si esto parece phishing"))
    payload = json.loads(raw)

    assert payload["routed_by"] == "strix_main_engine"
    assert payload["strix_main_engine_primary"] is True
    assert payload["saga_control_layer"] is True
    assert payload["workflow_category"] == "phishing_attachment"
    assert payload["execution_allowed"] is False


def test_defensive_command_router_is_not_primary_for_free_text_when_real_adapter_available():
    operator = _operator()
    operator.strix_agent_adapter = FakeAvailableAdapter()

    raw = asyncio.run(operator.handle_message("8166253211", "8166253211", "estado defensa"))
    payload = json.loads(raw)

    assert payload["routed_by"] == "real_strix_agent"
    assert payload["message"] == "respuesta desde STRIX real"
    assert payload["saga_control_layer"] is True


def test_explicit_slash_defensive_command_stays_legacy_control_path():
    operator = _operator()
    operator.strix_agent_adapter = FakeAvailableAdapter()

    raw = asyncio.run(operator.handle_message("8166253211", "8166253211", "/defense_status"))
    payload = json.loads(raw)

    assert payload["routed_by"] == "defensive_command_router_fallback"
    assert payload["workflow_category"] == "defense_status"
    assert payload["execution_allowed"] is False
