import types
from abc import ABC, abstractmethod
from .command_parser import CommandParser

class TelegramGateway(ABC):
    def __init__(self, config=None):
        self.config = config
        self.command_parser = CommandParser()

    """Abstract interface for Telegram communication."""
    
    @abstractmethod
    def send_message(self, chat_id: str, text: str) -> bool:
        """Send a text message."""
        pass

    @abstractmethod
    def send_document(self, chat_id: str, content: bytes, filename: str) -> bool:
        pass

    def handle_message(self, message) -> types.SimpleNamespace:
        """Handle incoming TelegramMessage-like objects."""
        user_id = getattr(message, "user_id", None)
        chat_id = getattr(message, "chat_id", None)
        text = getattr(message, "text", "") or ""
        allowed_user_ids = getattr(self.config, "allowed_user_ids", []) if self.config else []

        if user_id not in allowed_user_ids:
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
