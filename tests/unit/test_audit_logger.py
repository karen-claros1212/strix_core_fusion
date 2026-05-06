import pytest
from saga_fusion.audit_logger import SagaAuditLogger

def test_redact_ssh():
    logger = SagaAuditLogger()
    log = logger.log_action({"command": "cat ~/.ssh/id_rsa"})
    assert "id_rsa" in log.redacted_command

def test_redact_env():
    logger = SagaAuditLogger()
    log = logger.log_action({"command": "export API_KEY=12345"})
    assert "12345" not in log.redacted_command

def test_log_fingerprint():
    logger = SagaAuditLogger()
    decision = {"allowed": True, "risk_level": "high"}
    log = logger.log_decision(decision)
    assert log.fingerprint is not None
