import logging
import types
from abc import ABC, abstractmethod

from .command_parser import CommandParser
from .telegram_security import TelegramSecurity

logger = logging.getLogger(__name__)


class TelegramGateway(ABC):
    def __init__(self, config=None):
        self.config = config
        self.command_parser = CommandParser()
        self.security = TelegramSecurity(config=config)

    """Abstract interface for Telegram communication."""

    @abstractmethod
    def send_message(self, chat_id: str, text: str) -> bool:
        """Send a text message."""
        pass

    @abstractmethod
    def send_document(self, chat_id: str, content: bytes, filename: str) -> bool:
        pass

    def start(self) -> types.SimpleNamespace:
        if self.config is not None and not getattr(self.config, "is_ready", True):
            message = getattr(self.config, "config_error", "Telegram real mode disabled: incomplete configuration.")
            logger.warning(self.security.redact_secrets(message))
            return types.SimpleNamespace(ok=False, text=message)
        return types.SimpleNamespace(ok=True, text="Telegram gateway ready.")

    def handle_message(self, message) -> types.SimpleNamespace:
        """Handle incoming TelegramMessage-like objects."""
        user_id = getattr(message, "user_id", None)
        chat_id = getattr(message, "chat_id", None)
        text = getattr(message, "text", "") or ""

        if self.config is not None and not getattr(self.config, "is_ready", True):
            return types.SimpleNamespace(
                text=getattr(self.config, "config_error", "Telegram real mode disabled: incomplete configuration."),
                chat_id=chat_id,
            )

        if not self.security.validate_user(user_id):
            return types.SimpleNamespace(
                text="Usuario no autorizado.",
                chat_id=chat_id,
            )

        parsed = self.command_parser.parse(text)
        if parsed is None or not getattr(parsed, "known", False):
            return types.SimpleNamespace(
                text="Comando no reconocido.",
                chat_id=chat_id,
            )

        return types.SimpleNamespace(
            text="Mensaje recibido.",
            chat_id=chat_id,
        )
