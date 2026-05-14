from __future__ import annotations

import argparse
import asyncio
import json
import logging
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from typing import Any, Sequence

from .mission_operator import TelegramMissionOperator
from .telegram_config import TelegramConfig, load_telegram_config, validate_real_mode_config
from .telegram_gateway import TelegramGateway
from .telegram_security import TelegramSecurity

logger = logging.getLogger(__name__)


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

    def to_redacted_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["token"] = "[REDACTED]" if self.ok else ""
        return payload


class TelegramBotApi:
    """Minimal Bot API client for controlled lab polling.

    The token is read from TelegramConfig only and is never included in returned
    payloads or log messages.
    """

    def __init__(self, config: TelegramConfig, timeout_seconds: int = 20):
        self.config = config
        self.timeout_seconds = timeout_seconds
        self.security = TelegramSecurity(config)

    def _url(self, method: str) -> str:
        return f"https://api.telegram.org/bot{self.config.bot_token}/{method}"

    def request(self, method: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        body = json.dumps(payload or {}).encode("utf-8")
        request = urllib.request.Request(
            self._url(method),
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                data = response.read().decode("utf-8")
        except (urllib.error.URLError, TimeoutError) as exc:
            logger.warning("Telegram lab API call failed: %s", self.security.redact_secrets(exc))
            return {"ok": False, "description": "telegram_api_call_failed"}
        try:
            decoded = json.loads(data)
        except json.JSONDecodeError:
            return {"ok": False, "description": "telegram_api_invalid_json"}
        return decoded if isinstance(decoded, dict) else {"ok": False, "description": "telegram_api_invalid_payload"}


class TelegramLabRuntime:
    """Real Telegram transport wired to the existing lab/evidence-only defensive pipeline."""

    def __init__(
        self,
        config: TelegramConfig | None = None,
        *,
        api: TelegramBotApi | None = None,
        operator: TelegramMissionOperator | None = None,
        gateway: TelegramGateway | None = None,
    ):
        self.config = config or load_telegram_config()
        self.security = TelegramSecurity(self.config)
        self.gateway = gateway or TelegramGateway(config=self.config)
        self.operator = operator or TelegramMissionOperator(self.config, self.gateway)
        self.api = api or TelegramBotApi(self.config)
        self.evidence: list[dict[str, Any]] = []

    def preflight(self) -> TelegramLabPreflight:
        if getattr(self.config, "mode", "mock") != "real":
            return TelegramLabPreflight(
                ok=False,
                mode=getattr(self.config, "mode", "mock"),
                polling_enabled=getattr(self.config, "polling_enabled", False),
                webhook_enabled=getattr(self.config, "webhook_enabled", False),
                allowed_user_count=len(getattr(self.config, "allowed_user_ids", []) or []),
                reason="TELEGRAM_MODE must be real for live lab E2E",
            )
        ok, missing = validate_real_mode_config(self.config)
        if not ok:
            return TelegramLabPreflight(
                ok=False,
                mode=self.config.mode,
                polling_enabled=self.config.polling_enabled,
                webhook_enabled=self.config.webhook_enabled,
                allowed_user_count=len(self.config.allowed_user_ids),
                missing=tuple(missing),
                reason="missing required Telegram lab environment variables",
            )
        if not self.config.polling_enabled or self.config.webhook_enabled:
            return TelegramLabPreflight(
                ok=False,
                mode=self.config.mode,
                polling_enabled=self.config.polling_enabled,
                webhook_enabled=self.config.webhook_enabled,
                allowed_user_count=len(self.config.allowed_user_ids),
                reason="lab runtime requires polling enabled and webhook disabled",
            )
        bot_info = self.api.request("getMe", {})
        if not bot_info.get("ok"):
            return TelegramLabPreflight(
                ok=False,
                mode=self.config.mode,
                polling_enabled=self.config.polling_enabled,
                webhook_enabled=self.config.webhook_enabled,
                allowed_user_count=len(self.config.allowed_user_ids),
                reason=str(bot_info.get("description") or "getMe preflight failed"),
            )
        result = bot_info.get("result") if isinstance(bot_info.get("result"), dict) else {}
        return TelegramLabPreflight(
            ok=True,
            mode=self.config.mode,
            polling_enabled=self.config.polling_enabled,
            webhook_enabled=self.config.webhook_enabled,
            allowed_user_count=len(self.config.allowed_user_ids),
            bot_username=str(result.get("username") or ""),
            reason="preflight passed",
        )

    async def poll_once(self, *, offset: int | None = None, timeout_seconds: int = 20, limit: int = 10) -> tuple[int | None, int]:
        updates = self.api.request(
            "getUpdates",
            {
                "offset": offset,
                "timeout": timeout_seconds,
                "limit": limit,
                "allowed_updates": ["message"],
            },
        )
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
            message = update.get("message") if isinstance(update.get("message"), dict) else {}
            text = str(message.get("text") or "").strip()
            chat = message.get("chat") if isinstance(message.get("chat"), dict) else {}
            sender = message.get("from") if isinstance(message.get("from"), dict) else {}
            chat_id = str(chat.get("id") or "")
            user_id = str(sender.get("id") or "")
            if not text or not chat_id or not user_id:
                continue
            response = await self.operator.handle_message(chat_id, user_id, text)
            safe_response = self.security.redact_secrets(response)
            sent = self.api.request("sendMessage", {"chat_id": chat_id, "text": safe_response})
            self.evidence.append(
                {
                    "event": "telegram_lab_message",
                    "update_id": update_id,
                    "chat_id": self._redact_identifier(chat_id),
                    "user_id": self._redact_identifier(user_id),
                    "request_text": self.security.redact_secrets(text),
                    "response_preview": safe_response[:700],
                    "send_ok": sent.get("ok") is True,
                    "real_telegram_transport": True,
                    "execution_allowed": False,
                    "executed": False,
                    "non_authoritative": True,
                    "evidence_required": True,
                    "report_required": True,
                }
            )
            handled += 1
        return next_offset, handled

    async def latest_offset(self) -> int | None:
        updates = self.api.request("getUpdates", {"timeout": 0, "limit": 100, "allowed_updates": ["message"]})
        if not updates.get("ok"):
            self.evidence.append({"event": "initial_offset_failed", "description": updates.get("description")})
            return None
        max_update_id = None
        for update in updates.get("result", []) or []:
            if isinstance(update, dict) and isinstance(update.get("update_id"), int):
                max_update_id = update["update_id"] if max_update_id is None else max(max_update_id, update["update_id"])
        return (max_update_id + 1) if max_update_id is not None else None

    def acknowledge_offset(self, offset: int | None) -> bool:
        """Confirm handled Telegram updates before a bounded lab run exits.

        Telegram only marks updates as confirmed when a later getUpdates call
        supplies an offset greater than the handled update ids.  The lab runtime
        often exits immediately after max_messages is reached, so without this
        final zero-timeout acknowledgement the same already-answered messages
        remain pending and are answered again on the next bounded run.
        """
        if offset is None:
            return False
        ack = self.api.request(
            "getUpdates",
            {
                "offset": offset,
                "timeout": 0,
                "limit": 1,
                "allowed_updates": ["message"],
            },
        )
        ok = ack.get("ok") is True
        self.evidence.append({"event": "telegram_lab_ack", "offset": offset, "ack_ok": ok})
        return ok

    async def run(
        self,
        *,
        max_messages: int = 2,
        max_seconds: int = 120,
        poll_timeout_seconds: int = 15,
        start_at_latest: bool = False,
    ) -> dict[str, Any]:
        preflight = self.preflight()
        if not preflight.ok:
            return {"status": "no_go", "preflight": preflight.to_redacted_dict(), "evidence": self.evidence}
        offset: int | None = await self.latest_offset() if start_at_latest else None
        handled = 0
        deadline = time.time() + max_seconds
        while handled < max_messages and time.time() < deadline:
            offset, count = await self.poll_once(offset=offset, timeout_seconds=poll_timeout_seconds)
            handled += count
        if handled > 0:
            self.acknowledge_offset(offset)
        return {
            "status": "ok" if handled >= max_messages else "timeout",
            "preflight": preflight.to_redacted_dict(),
            "messages_handled": handled,
            "evidence": self.evidence,
        }

    async def run_service(
        self,
        *,
        poll_timeout_seconds: int = 15,
        start_at_latest: bool = False,
        idle_sleep_seconds: float = 0.0,
        max_polls: int | None = None,
    ) -> dict[str, Any]:
        """Run the lab poller as a persistent evidence-only service.

        ``max_polls`` is intentionally test-only; production service mode leaves it
        unset and relies on the process supervisor (for example systemd) for
        lifecycle and restart handling.
        """
        preflight = self.preflight()
        if not preflight.ok:
            return {"status": "no_go", "preflight": preflight.to_redacted_dict(), "evidence": self.evidence}

        offset: int | None = await self.latest_offset() if start_at_latest else None
        handled = 0
        polls = 0
        self.evidence.append(
            {
                "event": "telegram_lab_service_started",
                "bot_username": preflight.bot_username,
                "polling_enabled": preflight.polling_enabled,
                "webhook_enabled": preflight.webhook_enabled,
                "allowed_user_count": preflight.allowed_user_count,
                "execution_allowed": False,
                "executed": False,
                "non_authoritative": True,
                "evidence_required": True,
                "report_required": True,
            }
        )
        logger.info(
            "Telegram lab service started: %s",
            self.security.redact_secrets(
                {
                    "bot_username": preflight.bot_username,
                    "polling_enabled": preflight.polling_enabled,
                    "webhook_enabled": preflight.webhook_enabled,
                    "allowed_user_count": preflight.allowed_user_count,
                }
            ),
        )

        try:
            while max_polls is None or polls < max_polls:
                offset, count = await self.poll_once(offset=offset, timeout_seconds=poll_timeout_seconds)
                polls += 1
                handled += count
                if count > 0:
                    self.acknowledge_offset(offset)
                logger.info(
                    "Telegram lab service poll: %s",
                    self.security.redact_secrets({"polls": polls, "handled_total": handled, "handled_in_poll": count}),
                )
                if idle_sleep_seconds > 0:
                    await asyncio.sleep(idle_sleep_seconds)
        except asyncio.CancelledError:
            self.evidence.append({"event": "telegram_lab_service_cancelled", "polls": polls, "messages_handled": handled})
            raise

        return {
            "status": "ok",
            "service_mode": True,
            "preflight": preflight.to_redacted_dict(),
            "messages_handled": handled,
            "polls": polls,
            "evidence": self.evidence,
        }

    @staticmethod
    def _redact_identifier(value: str) -> str:
        text = str(value or "")
        return f"...{text[-4:]}" if len(text) > 4 else "[REDACTED]"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run STRIX Telegram lab E2E polling in evidence-only mode.")
    parser.add_argument("--service", action="store_true", help="Run continuously as a persistent lab poller; ignores bounded max options.")
    parser.add_argument("--max-messages", type=int, default=2, help="Bounded mode only: stop after this many handled messages.")
    parser.add_argument("--max-seconds", type=int, default=120, help="Bounded mode only: stop after this many seconds.")
    parser.add_argument("--poll-timeout-seconds", type=int, default=15)
    parser.add_argument("--idle-sleep-seconds", type=float, default=0.0, help="Service mode only: optional sleep between poll requests.")
    parser.add_argument("--start-at-latest", action="store_true", help="Ignore backlog and wait only for new lab messages.")
    return parser


def _configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    _configure_logging()

    runtime = TelegramLabRuntime()
    if args.service:
        result = asyncio.run(
            runtime.run_service(
                poll_timeout_seconds=max(1, args.poll_timeout_seconds),
                start_at_latest=args.start_at_latest,
                idle_sleep_seconds=max(0.0, args.idle_sleep_seconds),
            )
        )
    else:
        result = asyncio.run(
            runtime.run(
                max_messages=max(1, args.max_messages),
                max_seconds=max(5, args.max_seconds),
                poll_timeout_seconds=max(1, args.poll_timeout_seconds),
                start_at_latest=args.start_at_latest,
            )
        )
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.service and result.get("status") == "no_go":
        return 1
    return 0 if result.get("status") in {"ok", "timeout", "no_go"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
