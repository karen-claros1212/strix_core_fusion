from abc import ABC, abstractmethod
from typing import Dict, Any

class TelegramAdapter(ABC):
    @abstractmethod
    def get_updates(self, offset: int = None) -> list:
        """Fetch updates from Telegram."""
        pass

    @abstractmethod
    def send_message(self, chat_id: str, text: str, parse_mode: str = None) -> bool:
        """Send a message to a chat."""
        pass

    @abstractmethod
    def send_photo(self, chat_id: str, photo: bytes, caption: str = None) -> bool:
        """Send a photo to a chat."""
        pass

    @abstractmethod
    def send_document(self, chat_id: str, document: bytes, filename: str = None) -> bool:
        """Send a document to a chat."""
        pass
