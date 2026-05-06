import logging
import unittest
from unittest.mock import MagicMock

from saga_fusion.telegram.telegram_config import TelegramConfig
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
        self.config.allowed_user_ids = ["123"]
        self.config.allowed_users = ["123"]
        self.config.is_ready = True
        self.config.config_error = ""
        self.gateway = MockTelegramGateway(self.config)

    def test_missing_token_blocks_real_mode(self):
        config = TelegramConfig(bot_token="", allowed_user_ids=["123"])
        gateway = MockTelegramGateway(config)

        startup = gateway.start()
        response = gateway.handle_message(TelegramMessage(message_id=1, user_id=123, chat_id=1, text="/status"))

        self.assertFalse(startup.ok)
        self.assertIn("TELEGRAM_BOT_TOKEN", startup.text)
        self.assertIn("disabled", response.text.lower())

    def test_missing_allowed_users_blocks_real_mode(self):
        config = TelegramConfig(bot_token="123456:secret-token", allowed_user_ids=[])
        gateway = MockTelegramGateway(config)

        startup = gateway.start()

        self.assertFalse(startup.ok)
        self.assertIn("TELEGRAM_ALLOWED_USER_IDS", startup.text)

    def test_token_redacted_from_logs(self):
        config = TelegramConfig(bot_token="123456:ABC-secret", allowed_user_ids=[])
        gateway = MockTelegramGateway(config)

        with self.assertLogs("saga_fusion.telegram.telegram_gateway", level=logging.WARNING) as captured:
            gateway.start()

        log_output = "\n".join(captured.output)
        self.assertNotIn("123456:ABC-secret", log_output)

    def test_unauthorized_user_blocked(self):
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
