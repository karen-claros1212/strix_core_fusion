import unittest

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
        text = "api_" + "key=" + "secret123"
        redacted = self.security.redact_secrets(text)
        self.assertNotIn("secret123", redacted)
        self.assertIn("REDACTED", redacted)

    def test_redact_token(self):
        text = "token 123456:abcXYZ"
        redacted = self.security.redact_secrets(text)
        self.assertNotIn("123456:abcXYZ", redacted)
        self.assertIn("REDACTED", redacted)

    def test_rate_limit(self):
        for _ in range(5):
            self.assertTrue(self.security.check_rate_limit(123))
        self.assertFalse(self.security.check_rate_limit(123))


if __name__ == '__main__':
    unittest.main()
