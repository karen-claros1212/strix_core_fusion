"""Direct handler: Telegram message to official STRIX agent (no Saga Fusion as engine)."""

from __future__ import annotations
import asyncio, logging
from typing import Any

_log = logging.getLogger(__name__)

class OfficialStrixDirectHandler:
    def __init__(self) -> None:
        self._gateway: Any = None
        self._init_gateway()

    def _init_gateway(self) -> None:
        try:
            from strix_bridge.integrations.telegram.strix_core_gateway import StrixCoreGateway
            self._gateway = StrixCoreGateway(enabled=True)
            _log.info("OfficialStrixDirectHandler: StrixCoreGateway ready")
        except Exception as exc:
            _log.error("OfficialStrixDirectHandler: failed to init gateway: %s", exc)
            self._gateway = None

    @property
    def available(self) -> bool:
        return self._gateway is not None and self._gateway.is_available()

    async def handle_message(self, chat_id: str, user_id: str, text: str) -> str:
        text = (text or "").strip()
        if not text:
            return "STRIX_ERROR:EMPTY_MESSAGE"
        if self._gateway is None:
            return "STRIX_ERROR:STRIX_GATEWAY_UNAVAILABLE"
        try:
            result = await asyncio.wait_for(self._gateway.handle_message(chat_id, user_id, text), timeout=120.0)
        except asyncio.TimeoutError:
            return "STRIX_ERROR:STRIX_AGENT_TIMEOUT"
        except Exception as exc:
            return f"STRIX_ERROR:STRIX_AGENT_ERROR:{type(exc).__name__}"
        if not result.available:
            return f"STRIX_ERROR:STRIX_OFFICIAL_UNAVAILABLE:{result.reason}"
        if not result.handled:
            return f"STRIX_ERROR:STRIX_NOT_HANDLED:{result.reason}"
        response = (result.response or "").strip()
        if not response:
            return "STRIX_ERROR:STRIX_EMPTY_RESPONSE"
        return response
