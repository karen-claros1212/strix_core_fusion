"""
official_strix_direct_handler.py
─────────────────────────────────
Handler directo Telegram → StrixCoreGateway.

Fusión limpia: un solo path, sin fallback a Saga/operator.
Si STRIX no responde → error claro, no silencio.
"""

from __future__ import annotations

import asyncio
import logging

_log = logging.getLogger(__name__)

# Timeout total desde que llega el mensaje hasta que se envía la respuesta.
# 90s para el agente + margen de red.
_HANDLER_TIMEOUT = 110.0


class OfficialStrixDirectHandler:
    def __init__(self):
        self._gateway = None
        self._init_gateway()

    def _init_gateway(self) -> None:
        try:
            from strix_bridge.integrations.telegram.strix_core_gateway import StrixCoreGateway  # noqa: PLC0415
            self._gateway = StrixCoreGateway(enabled=True, agent_timeout=180.0)
            _log.info("OfficialStrixDirectHandler: gateway listo")
        except Exception as exc:
            _log.error("OfficialStrixDirectHandler: no pudo iniciar gateway — %s", exc)
            self._gateway = None

    @property
    def available(self) -> bool:
        return self._gateway is not None and self._gateway.is_available()

    async def handle_message(self, chat_id, user_id, text: str) -> str:
        text = (text or "").strip()
        if not text:
            return "STRIX_ERROR:EMPTY_MESSAGE"
        if self._gateway is None:
            return "STRIX_ERROR:GATEWAY_UNAVAILABLE"

        try:
            result = await asyncio.wait_for(
                self._gateway.handle_message(chat_id, user_id, text),
                timeout=_HANDLER_TIMEOUT,
            )
        except asyncio.TimeoutError:
            _log.warning("OfficialStrixDirectHandler: timeout total (%.0fs) chat_id=%s", _HANDLER_TIMEOUT, chat_id)
            return "STRIX_ERROR:TIMEOUT"
        except Exception as exc:
            _log.exception("OfficialStrixDirectHandler: error inesperado")
            return f"STRIX_ERROR:{type(exc).__name__}"

        if not result.available:
            return f"STRIX_ERROR:UNAVAILABLE:{result.reason}"
        if not result.handled:
            return f"STRIX_ERROR:NOT_HANDLED:{result.reason}"

        response = (result.response or "").strip()
        return response if response else "STRIX_ERROR:EMPTY_RESPONSE"
