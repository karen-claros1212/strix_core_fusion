import re
import shlex
import hashlib
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

@dataclass
class SecurityDecision:
    allowed: bool
    reason: str
    severity: str # LOW, MEDIUM, HIGH, CRITICAL
    sanitized_action: Optional[Dict[str, Any]]
    redacted_fingerprint: str

class SagaSecurityPolicy:
    def __init__(self):
        self.logger = logging.getLogger("Saga.SecurityPolicy")
        self.denylist = [
            r'cat\s+/dev/(tcp|udp)',
            r'curl.*\/dev\/(tcp|udp)',
            r'rm\s+-rf\s+/\*|rm\s+-rf\s+/.*',
            r'!\s*bash',
            r'mkfifo',
            r'chmod\s+777'
        ]
        self.allowlist = [
            r'^ls',
            r'^cat\s',
            r'^echo\s',
            r'^pwd'
        ]
    
    def normalize_command(self, cmd: str) -> str:
        """Normaliza el comando usando shlex para manejar espacios y comillas correctamente."""
        try:
            return shlex.quote(cmd)
        except Exception as e:
            self.logger.warning(f"Error normalizando comando: {e}")
            return cmd

    def evaluate_action(self, action: Dict[str, Any]) -> SecurityDecision:
        cmd = action.get('command', '')
        normalized = self.normalize_command(cmd)
        
        # Check denylist
        for pattern in self.denylist:
            if re.search(pattern, cmd):
                return SecurityDecision(
                    allowed=False,
                    reason=f"Denylist match: {pattern}",
                    severity="HIGH",
                    sanitized_action=None,
                    redacted_fingerprint=hashlib.sha256(cmd.encode()).hexdigest()[:8]
                )
        
        # Check allowlist
        for pattern in self.allowlist:
            if re.search(pattern, cmd):
                return SecurityDecision(
                    allowed=True,
                    reason="Allowlist match",
                    severity="LOW",
                    sanitized_action=action,
                    redacted_fingerprint=hashlib.sha256(cmd.encode()).hexdigest()[:8]
                )
        
        # Default deny
        return SecurityDecision(
            allowed=False,
            reason="Default deny policy",
            severity="MEDIUM",
            sanitized_action=None,
            redacted_fingerprint=hashlib.sha256(cmd.encode()).hexdigest()[:8]
        )
