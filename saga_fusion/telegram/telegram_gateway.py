import json
import logging
import types
import urllib.error
import urllib.parse
import urllib.request

from saga_fusion.runtime.output_budget import SagaOutputBudget

from .command_parser import CommandParser
from .telegram_config import TelegramConfig, load_telegram_config, validate_real_mode_config
from .telegram_security import TelegramSecurity

logger = logging.getLogger(__name__)


class TelegramGateway:
    def __init__(self, config: TelegramConfig | None = None, api_client=None):
        self.config = config or load_telegram_config()
        self.command_parser = CommandParser()
        self.security = TelegramSecurity(config=self.config)
        self.output_budget = SagaOutputBudget(max_chars=4000, preserve_head=1500, preserve_tail=2500)
        self.api_client = api_client
        self.running = False

    def _safe_error(self) -> str:
        return getattr(self.config, "config_error", "Telegram real mode disabled: incomplete configuration.")

    def _validate_startup(self) -> tuple[bool, str]:
        if getattr(self.config, "mode", "mock") == "real":
            ok, _missing = validate_real_mode_config(self.config)
            if not ok:
                return False, self._safe_error()
        return True, "Telegram gateway ready."

    def start(self) -> types.SimpleNamespace:
        ok, message = self._validate_startup()
        if not ok:
            logger.warning(self.security.redact_secrets(message))
            self.running = False
            return types.SimpleNamespace(ok=False, text=message)
        self.running = True
        return types.SimpleNamespace(ok=True, text=message)

    def stop(self) -> types.SimpleNamespace:
        self.running = False
        return types.SimpleNamespace(ok=True, text="Telegram gateway stopped.")

    def handle_message(self, message) -> types.SimpleNamespace:
        user_id = getattr(message, "user_id", None)
        chat_id = getattr(message, "chat_id", None)
        text = getattr(message, "text", "") or ""

        if getattr(self.config, "mode", "mock") == "real" and not getattr(self.config, "is_ready", False):
            return types.SimpleNamespace(text=self._safe_error(), chat_id=chat_id, ok=False)

        if not self.security.check_rate_limit(user_id):
            return types.SimpleNamespace(text="Rate limit exceeded.", chat_id=chat_id, ok=False)

        if not self.security.validate_user(user_id):
            return types.SimpleNamespace(text="DENIED: usuario no autorizado.", chat_id=chat_id, ok=False)

        parsed = self.command_parser.parse(text)
        if parsed is None or not getattr(parsed, "known", False):
            return types.SimpleNamespace(text="Comando no reconocido.", chat_id=chat_id, ok=False)

        return types.SimpleNamespace(text="Mensaje recibido.", chat_id=chat_id, ok=True)

    def _api_url(self, method: str) -> str:
        return f"https://api.telegram.org/bot{self.config.bot_token}/{method}"

    def _post_json(self, method: str, payload: dict) -> bool:
        if getattr(self.config, "mode", "mock") != "real":
            return True
        ok, error = self._validate_startup()
        if not ok:
            logger.warning(self.security.redact_secrets(error))
            return False
        if self.api_client is not None:
            return bool(self.api_client(method, payload))
        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            self._api_url(method),
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                return 200 <= response.status < 300
        except (urllib.error.URLError, TimeoutError) as exc:
            logger.warning("Telegram API call failed: %s", self.security.redact_secrets(exc))
            return False

    def send_message(self, chat_id: str, text: str) -> bool:
        _raw, model_view = self.output_budget.split_raw_and_model_view(str(text), "telegram", "message")
        safe_text = self.security.redact_secrets(model_view)
        if getattr(self.config, "mode", "mock") == "mock":
            return True
        return self._post_json("sendMessage", {"chat_id": str(chat_id), "text": safe_text})

    def send_document(self, chat_id: str, content: bytes, filename: str) -> bool:
        if getattr(self.config, "mode", "mock") == "mock":
            return True
        ok, error = self._validate_startup()
        if not ok:
            logger.warning(self.security.redact_secrets(error))
            return False
        if self.api_client is not None:
            return bool(self.api_client("sendDocument", {"chat_id": str(chat_id), "filename": filename, "content": content}))
        # Real multipart upload intentionally remains client-injectable until live preflight.
        logger.warning("Telegram real document upload requires injected API client; refusing unsafe fallback.")
        return False
