import pytest
from saga_fusion.audit_logger import SagaAuditLogger

class TestSecretRedaction:
    def setup_method(self):
        self.logger = SagaAuditLogger()

    def test_redact_ssh(self):
        data = {"output": "-----BEGIN RSA PRIVATE KEY-----"}
        redacted = self.logger.redact_secrets(data)
        assert "-----BEGIN RSA PRIVATE KEY-----" not in redacted.get("output", "")

    def test_redact_env(self):
        data = {"command": "export API_KEY=secret123"}
        redacted = self.logger.redact_secrets(data)
        assert "secret123" not in redacted.get("command", "")

    def test_redact_api_keys(self):
        data = {"command": "curl -H 'Authorization: Bearer token123'"}
        redacted = self.logger.redact_secrets(data)
        assert "Bearer token123" not in redacted.get("command", "")

    def test_register_fingerprint(self):
        decision = {"allowed": True, "command": "ls"}
        log = self.logger.log_decision(decision)
        assert log.fingerprint is not None
        assert len(log.fingerprint) == 8
        assert all(c in '0123456789abcdef' for c in log.fingerprint)
