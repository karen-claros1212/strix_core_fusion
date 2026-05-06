import re
import hashlib
from typing import Optional
import logging

logger = logging.getLogger(__name__)
import logging
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class AuditLog:
    timestamp: str
    action: str
    decision: str
    redacted_command: Optional[str] = None
    fingerprint: Optional[str] = None

class SagaAuditLogger:
    def __init__(self):
        self.logger = logging.getLogger("Saga.AuditLogger")

    def redact_secrets(self, data):
        """Redact sensitive information in a dictionary or string."""
        if isinstance(data, str):
            return self._redact_str(data)
        if not isinstance(data, dict):
            return data
        
        redacted = {}
        for key, value in data.items():
            if isinstance(value, str):
                # Fix regex: use explicit groups or simple replacement
                patterns = [
                    (r'-----BEGIN (?:RSA |DSA |EC )?PRIVATE KEY-----', '[REDACTED_KEY]'),
                    (r'-----END (?:RSA |DSA |EC )?PRIVATE KEY-----', '[REDACTED_KEY]'),
                    (r'(?i)api[_-]?key\s*[=:]\s*([a-zA-Z0-9_-]+)', r'api_key=[REDACTED]'),
                    (r'(?i)token\s*[=:]\s*([a-zA-Z0-9_-]+)', r'token=[REDACTED]'),
                    (r'(?i)authorization\s*:\s*Bearer\s+([a-zA-Z0-9._-]+)', r'Authorization: Bearer [REDACTED]'),
                    (r'(?i)password\s*[=:]\s*(\S+)', r'password=[REDACTED]'),
                ]
                for pattern, replacement in patterns:
                    value = re.sub(pattern, replacement, value)
                redacted[key] = value
            elif isinstance(value, dict):
                redacted[key] = self.redact_secrets(value)
            elif isinstance(value, list):
                redacted[key] = [self.redact_secrets(item) if isinstance(item, dict) else item for item in value]
            else:
                redacted[key] = value
        return redacted
    def _redact_str(self, text: str) -> str:
        """Redact secrets in a string."""
        if not isinstance(text, str):
            return text
        patterns = [
            r'(?i)(api[_-]?key\s*=\s*)\S+',
            r'(?i)(key\s*=\s*)\S+',
            r'(?i)(password\s*=\s*)\S+',
            r'(?i)(secret\s*=\s*)\S+',
            r'(?i)(authorization\s*:\s*)\S+',
            r'(~[/]\.ssh)',
            r'(-----BEGIN.*PRIVATE KEY-----)'
        ]
        for pattern in patterns:
            text = re.sub(pattern, r'[REDACTED]', text)
        return text

    def log_action(self, action: Dict[str, Any] = None, action_type: str = "command", decision: str = "PENDING", policy_id: str = "", command: str = "") -> AuditLog:
        cmd = command if command else (action.get('command', '') if action else '')
        redacted_cmd = self.redact_secrets(cmd)
        fingerprint = hashlib.sha256(str(cmd).encode()).hexdigest()[:8]
        
        log_entry = AuditLog(
            timestamp=datetime.now().isoformat(),
            action=action_type,
            decision=decision,
            redacted_command=redacted_cmd,
            fingerprint=fingerprint
        )
        self.logger.info(f"[{policy_id}] Action [{action_type}] logged: {redacted_cmd}")
        return log_entry

    def log_decision(self, decision: dict, action: Optional[str] = None) -> AuditLog:
        """Log a decision and redact secrets."""
        content_for_hash = str(decision.get('command', decision.get('action', '')))
        fingerprint = hashlib.sha256(content_for_hash.encode()).hexdigest()[:8]
        log_entry = AuditLog(
            timestamp=datetime.now().isoformat(),
            action=action or decision.get('action', 'unknown'),
            decision='PENDING',
            fingerprint=fingerprint
        )
        logger.info(f"Decision logged: {log_entry.fingerprint}")
        return log_entry

    def _redact(self, text: str) -> str:
        return self.redact_secrets(text)

