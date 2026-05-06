import unittest
import time
from saga_fusion.telegram.telegram_security import TelegramSecurity

class TestTelegramSecurity(unittest.TestCase):
    def setUp(self):
        self.security = TelegramSecurity(allowed_user_ids=[123, 456], rate_limit=5)

    def test_validate_user_allowed(self):
        self.assertTrue(self.security.validate_user(123))
        self.assertTrue(self.security.validate_user(456))

    def test_validate_user_denied(self):
        self.assertFalse(self.security.validate_user(789))

    def test_redact_api_key(self):
        text = "api_key=secret123"
        redacted = self.security.redact_secrets(text)
        self.assertIn("api_key=***", redacted)

    def test_redact_token(self):
        text = "token abc123xyz"
        redacted = self.security.redact_secrets(text)
        self.assertIn("token ***", redacted)

    def test_rate_limit(self):
        # Allow 5 requests
        for _ in range(5):
            self.assertTrue(self.security.check_rate_limit(123))
        # 6th request should fail
        self.assertFalse(self.security.check_rate_limit(123))

if __name__ == '__main__':
    unittest.main()