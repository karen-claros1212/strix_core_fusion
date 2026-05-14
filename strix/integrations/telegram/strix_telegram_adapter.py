from __future__ import annotations

from .strix_core_gateway import StrixCoreGateway, StrixCoreGatewayResult


class StrixTelegramAdapter(StrixCoreGateway):
    """Telegram-facing adapter for the canonical STRIX Core gateway."""


StrixTelegramAdapterResult = StrixCoreGatewayResult

__all__ = ["StrixTelegramAdapter", "StrixTelegramAdapterResult"]
