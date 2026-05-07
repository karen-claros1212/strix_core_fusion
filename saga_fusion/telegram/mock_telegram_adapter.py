from .telegram_gateway import TelegramGateway
from .telegram_config import TelegramConfig


class MockTelegramAdapter(TelegramGateway):
    def __init__(self, config=None):
        super().__init__(config=config or TelegramConfig(mode="mock"))
        self.messages = []
        self.documents = []

    def send_message(self, chat_id: str, text: str) -> bool:
        safe_text = self.security.redact_secrets(text)
        self.messages.append({"chat_id": chat_id, "text": safe_text})
        return True

    def send_document(self, chat_id: str, content: bytes, filename: str) -> bool:
        self.documents.append({"chat_id": chat_id, "content": content, "filename": filename})
        return True
