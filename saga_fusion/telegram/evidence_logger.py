from datetime import datetime
from .telegram_types import MissionRequest
from .telegram_audit import TelegramAudit
from .telegram_security import TelegramSecurity


class EvidenceLogger:
    def __init__(self, audit: TelegramAudit | None, security: TelegramSecurity):
        self.audit = audit
        self.security = security
        self.records = []

    def log_mission(self, request: MissionRequest, result: dict):
        """Log a mission request and its result."""
        redacted_arguments = self.security.redact_secrets(request.arguments).replace('***', 'REDACTED')
        log_data = {
            'mission_id': request.mission_id,
            'requester_id': request.requester_id,
            'chat_id': request.chat_id,
            'action_type': request.action_type,
            'target': request.target,
            'arguments': redacted_arguments,
            'risk_level': request.risk_level.value,
            'status': request.status.value,
            'result': result,
            'timestamp': datetime.utcnow().isoformat()
        }
        self.records.append(log_data)
        if self.audit:
            if hasattr(self.audit, 'log_event'):
                self.audit.log_event('mission', log_data)
            elif hasattr(self.audit, 'log'):
                self.audit.log(request.chat_id, request.requester_id, 'mission', log_data)
        return log_data
