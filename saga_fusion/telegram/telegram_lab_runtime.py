"""
telegram_lab_runtime.py
────────────────────────
Poller Telegram → OfficialStrixDirectHandler → sendMessage.

Fusión limpia:
- Un solo path de mensajes: STRIX directo.
- Sin fallback a TelegramMissionOperator / Saga.
- Si STRIX falla → responde el error al usuario (visible, no silencio).
- run_service() corre indefinidamente hasta CancelledError.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass

from strix_bridge.integrations.telegram.official_strix_direct_handler import OfficialStrixDirectHandler
from .telegram_config import TelegramConfig, load_telegram_config, validate_real_mode_config
from .telegram_security import TelegramSecurity

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# Preflight
# ──────────────────────────────────────────────

@dataclass(frozen=True)
class TelegramLabPreflight:
    ok: bool
    mode: str
    polling_enabled: bool
    webhook_enabled: bool
    allowed_user_count: int
    missing: tuple[str, ...] = ()
    bot_username: str = ""
    reason: str = ""

    def to_redacted_dict(self):
        return {**asdict(self), "token": "[REDACTED]"}


# ──────────────────────────────────────────────
# API wrapper mínimo
# ──────────────────────────────────────────────

class TelegramBotApi:
    def __init__(self, config: TelegramConfig, timeout_seconds: int = 20):
        self.config = config
        self.timeout_seconds = timeout_seconds
        self.security = TelegramSecurity(config)

    def _url(self, method: str) -> str:
        return f"https://api.telegram.org/bot{self.config.bot_token}/{method}"

    def request(self, method: str, payload: dict | None = None) -> dict:
        body = json.dumps(payload or {}).encode("utf-8")
        req = urllib.request.Request(
            self._url(method),
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as resp:
                data = resp.read().decode("utf-8")
        except (urllib.error.URLError, TimeoutError) as exc:
            logger.warning("Telegram API call failed: %s", self.security.redact_secrets(str(exc)))
            return {"ok": False, "description": "api_call_failed"}
        try:
            decoded = json.loads(data)
        except json.JSONDecodeError:
            return {"ok": False, "description": "invalid_json"}
        return decoded if isinstance(decoded, dict) else {"ok": False, "description": "invalid_payload"}


# ──────────────────────────────────────────────
# Runtime principal
# ──────────────────────────────────────────────

class TelegramLabRuntime:
    def __init__(self, config: TelegramConfig | None = None, *, api: TelegramBotApi | None = None):
        self.config = config or load_telegram_config()
        self.security = TelegramSecurity(self.config)
        self.api = api or TelegramBotApi(self.config)
        self.handler = OfficialStrixDirectHandler()
        self.evidence: list[dict] = []

    # ── Preflight ────────────────────────────────────────────────────────

    def preflight(self) -> TelegramLabPreflight:
        mode = getattr(self.config, "mode", "mock")
        polling_enabled = getattr(self.config, "polling_enabled", False)
        webhook_enabled = getattr(self.config, "webhook_enabled", False)
        allowed = len(getattr(self.config, "allowed_user_ids", []) or [])

        if mode != "real":
            return TelegramLabPreflight(ok=False, mode=mode, polling_enabled=polling_enabled, webhook_enabled=webhook_enabled, allowed_user_count=allowed, reason="TELEGRAM_MODE must be 'real'")

        ok, missing = validate_real_mode_config(self.config)
        if not ok:
            return TelegramLabPreflight(ok=False, mode=mode, polling_enabled=polling_enabled, webhook_enabled=webhook_enabled, allowed_user_count=allowed, missing=tuple(missing), reason="missing required env vars")

        if not polling_enabled or webhook_enabled:
            return TelegramLabPreflight(ok=False, mode=mode, polling_enabled=polling_enabled, webhook_enabled=webhook_enabled, allowed_user_count=allowed, reason="polling must be enabled and webhook disabled")

        bot_info = self.api.request("getMe", {})
        if not bot_info.get("ok"):
            return TelegramLabPreflight(ok=False, mode=mode, polling_enabled=polling_enabled, webhook_enabled=webhook_enabled, allowed_user_count=allowed, reason=str(bot_info.get("description") or "getMe failed"))

        result = bot_info.get("result") or {}
        return TelegramLabPreflight(ok=True, mode=mode, polling_enabled=polling_enabled, webhook_enabled=webhook_enabled, allowed_user_count=allowed, bot_username=str(result.get("username") or ""), reason="preflight_ok")

    # ── Poll cycle ───────────────────────────────────────────────────────

    async def poll_once(self, *, offset: int | None = None, timeout_seconds: int = 20, limit: int = 10) -> tuple[int | None, int]:
        updates = self.api.request("getUpdates", {"offset": offset, "timeout": timeout_seconds, "limit": limit, "allowed_updates": ["message"]})
        if not updates.get("ok"):
            self.evidence.append({"event": "get_updates_failed", "description": updates.get("description")})
            return offset, 0

        handled = 0
        next_offset = offset

        for update in updates.get("result", []) or []:
            if not isinstance(update, dict):
                continue

            update_id = update.get("update_id")
            if isinstance(update_id, int):
                next_offset = update_id + 1

            message = update.get("message") or {}
            if not isinstance(message, dict):
                continue

            text = str(message.get("text") or "").strip()
            chat = message.get("chat") or {}
            sender = message.get("from") or {}
            chat_id = str(chat.get("id") or "")
            user_id = str(sender.get("id") or "")

            if not text or not chat_id or not user_id:
                continue

            logger.info("Mensaje recibido chat_id=%s user_id=%s texto=%r", self._redact(chat_id), self._redact(user_id), text[:80])

            # ── Path único: STRIX directo ──
            response = await self.handler.handle_message(chat_id, user_id, text)

            safe_response = self.security.redact_secrets(response)
            sent = self.api.request("sendMessage", {"chat_id": chat_id, "text": safe_response})

            self.evidence.append({
                "event": "message_handled",
                "update_id": update_id,
                "chat_id": self._redact(chat_id),
                "user_id": self._redact(user_id),
                "text_preview": self.security.redact_secrets(text[:80]),
                "response_preview": safe_response[:200],
                "send_ok": sent.get("ok") is True,
            })

            if not sent.get("ok"):
                logger.warning("sendMessage falló: %s", sent.get("description"))

            handled += 1

        return next_offset, handled

    # ── Offset helpers ───────────────────────────────────────────────────

    async def latest_offset(self) -> int | None:
        updates = self.api.request("getUpdates", {"timeout": 0, "limit": 100, "allowed_updates": ["message"]})
        if not updates.get("ok"):
            return None
        max_id = None
        for u in updates.get("result", []) or []:
            if isinstance(u, dict) and isinstance(u.get("update_id"), int):
                max_id = u["update_id"] if max_id is None else max(max_id, u["update_id"])
        return (max_id + 1) if max_id is not None else None

    def acknowledge_offset(self, offset: int | None) -> bool:
        if offset is None:
            return False
        ack = self.api.request("getUpdates", {"offset": offset, "timeout": 0, "limit": 1, "allowed_updates": ["message"]})
        return ack.get("ok") is True

    # ── run() — modo batch ───────────────────────────────────────────────

    async def run(self, *, max_messages: int = 2, max_seconds: int = 120, poll_timeout_seconds: int = 15, start_at_latest: bool = False) -> dict:
        preflight = self.preflight()
        if not preflight.ok:
            return {"status": "no_go", "preflight": preflight.to_redacted_dict(), "evidence": self.evidence}

        offset = await self.latest_offset() if start_at_latest else None
        handled = 0
        deadline = time.time() + max_seconds

        while handled < max_messages and time.time() < deadline:
            offset, count = await self.poll_once(offset=offset, timeout_seconds=poll_timeout_seconds)
            handled += count

        if handled > 0:
            self.acknowledge_offset(offset)

        return {"status": "ok" if handled >= max_messages else "timeout", "preflight": preflight.to_redacted_dict(), "messages_handled": handled, "evidence": self.evidence}

    # ── run_service() — modo daemon ──────────────────────────────────────

    async def run_service(self, *, poll_timeout_seconds: int = 15, start_at_latest: bool = False, idle_sleep_seconds: float = 0.0, max_polls: int | None = None) -> dict:
        preflight = self.preflight()
        if not preflight.ok:
            return {"status": "no_go", "preflight": preflight.to_redacted_dict(), "evidence": self.evidence}

        offset = await self.latest_offset() if start_at_latest else None
        handled = 0
        polls = 0

        logger.info("Telegram runtime iniciado — bot: %s", preflight.bot_username)
        self.evidence.append({"event": "service_started", "bot_username": preflight.bot_username})

        try:
            while max_polls is None or polls < max_polls:
                offset, count = await self.poll_once(offset=offset, timeout_seconds=poll_timeout_seconds)
                polls += 1
                handled += count
                if count > 0:
                    self.acknowledge_offset(offset)
                logger.info("poll=%d total_mensajes=%d este_poll=%d", polls, handled, count)
                if idle_sleep_seconds > 0:
                    await asyncio.sleep(idle_sleep_seconds)
        except asyncio.CancelledError:
            self.evidence.append({"event": "service_cancelled", "polls": polls, "messages_handled": handled})
            raise

        return {"status": "ok", "service_mode": True, "preflight": preflight.to_redacted_dict(), "messages_handled": handled, "polls": polls, "evidence": self.evidence}

    @staticmethod
    def _redact(value: str) -> str:
        return f"...{value[-4:]}" if len(value) > 4 else "[REDACTED]"


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Telegram → STRIX runtime")
    p.add_argument("--service", action="store_true", help="Modo daemon (indefinido)")
    p.add_argument("--max-messages", type=int, default=2)
    p.add_argument("--max-seconds", type=int, default=120)
    p.add_argument("--poll-timeout-seconds", type=int, default=15)
    p.add_argument("--idle-sleep-seconds", type=float, default=0.0)
    p.add_argument("--start-at-latest", action="store_true")
    return p


def main(argv=None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    args = _build_parser().parse_args(argv)
    runtime = TelegramLabRuntime()

    if args.service:
        result = asyncio.run(runtime.run_service(
            poll_timeout_seconds=max(1, args.poll_timeout_seconds),
            start_at_latest=args.start_at_latest,
            idle_sleep_seconds=max(0.0, args.idle_sleep_seconds),
        ))
    else:
        result = asyncio.run(runtime.run(
            max_messages=max(1, args.max_messages),
            max_seconds=max(5, args.max_seconds),
            poll_timeout_seconds=max(1, args.poll_timeout_seconds),
            start_at_latest=args.start_at_latest,
        ))

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("status") in {"ok", "timeout", "no_go"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
