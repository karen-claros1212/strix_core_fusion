from .telegram_gateway import TelegramGateway

class MockTelegramAdapter(TelegramGateway):
    def __init__(self):
        self.messages = []
        self.documents = []

    def send_message(self, chat_id: str, text: str) -> bool:
        self.messages.append({'chat_id': chat_id, 'text': text})
        return True

    def send_document(self, chat_id: str, content: bytes, filename: str) -> bool:
        self.documents.append({'chat_id': chat_id, 'content': content, 'filename': filename})
        return True
