from __future__ import annotations

from typing import Any

from .strix_telegram_adapter import StrixTelegramAdapter


class StrixTelegramRouter:
    """Thin router that sends Telegram free text to STRIX Core first."""

    def __init__(self, adapter: StrixTelegramAdapter | None = None):
        self.adapter = adapter or StrixTelegramAdapter()

    async def route(self, chat_id: str, user_id: str, text: str) -> Any:
        return await self.adapter.handle_message(chat_id, user_id, text)


__all__ = ["StrixTelegramRouter"]
