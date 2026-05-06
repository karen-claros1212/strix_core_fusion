import unittest
from unittest.mock import MagicMock
from saga_fusion.telegram.telegram_gateway import TelegramGateway
from saga_fusion.telegram.telegram_types import TelegramMessage

class MockTelegramGateway(TelegramGateway):
    def send_message(self, chat_id, text):
        return True
    def send_document(self, chat_id, content, filename):
        return True

class TestTelegramGateway(unittest.TestCase):
    def setUp(self):
        self.config = MagicMock()
        self.config.allowed_user_ids = [123]
        self.gateway = MockTelegramGateway(self.config)

    def test_handle_message_unauthorized_user(self):
        msg = TelegramMessage(message_id=1, user_id=456, chat_id=1, text="/status")
        response = self.gateway.handle_message(msg)
        self.assertIn("no autorizado", response.text.lower())

    def test_handle_message_unknown_command(self):
        msg = TelegramMessage(message_id=1, user_id=123, chat_id=1, text="hello")
        response = self.gateway.handle_message(msg)
        self.assertIn("comando no reconocido", response.text.lower())

    def test_handle_message_valid_command(self):
        msg = TelegramMessage(message_id=1, user_id=123, chat_id=1, text="/status")
        response = self.gateway.handle_message(msg)
        self.assertIsNotNone(response)
        self.assertEqual(response.chat_id, 1)

if __name__ == '__main__':
    unittest.main()