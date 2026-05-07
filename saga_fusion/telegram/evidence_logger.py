from datetime import datetime
from .telegram_types import MissionRequest
from .telegram_audit import TelegramAudit
from .telegram_security import TelegramSecurity


class EvidenceLogger:
    def __init__(self, audit: TelegramAudit | None, security: TelegramSecurity):
        self.audit = audit
        self.security = security
        self.records = []

    def _record(self, event_type: str, data: dict):
        redacted = self._redact_mapping(data)
        redacted["event_type"] = event_type
        redacted["timestamp"] = datetime.utcnow().isoformat()
        self.records.append(redacted)
        if self.audit:
            if hasattr(self.audit, "log_event"):
                self.audit.log_event(event_type, redacted)
            elif hasattr(self.audit, "log"):
                self.audit.log(redacted.get("chat_id"), redacted.get("user_id"), event_type, redacted)
        return redacted

    def _redact_mapping(self, value):
        if isinstance(value, dict):
            return {key: self._redact_mapping(val) for key, val in value.items()}
        if isinstance(value, list):
            return [self._redact_mapping(item) for item in value]
        if isinstance(value, str):
            return self.security.redact_secrets(value).replace("[REDACTED]", "REDACTED")
        return value

    def log_incoming_message(self, chat_id, user_id, text):
        return self._record("incoming_message", {"chat_id": str(chat_id), "user_id": str(user_id), "text": text})

    def log_authorization_decision(self, chat_id, user_id, allowed: bool):
        return self._record("authorization_decision", {"chat_id": str(chat_id), "user_id": str(user_id), "allowed": bool(allowed)})

    def log_approval_decision(self, approval_id, decision: str, action_hash: str | None = None):
        return self._record("approval_decision", {"approval_id": approval_id, "decision": decision, "action_hash": action_hash})

    def log_policy_decision(self, mission_id, risk_level, decision: str):
        risk_value = getattr(risk_level, "value", str(risk_level))
        return self._record("policy_decision", {"mission_id": mission_id, "risk_level": risk_value, "decision": decision})

    def log_sandbox_dispatch_result(self, mission_id, result: dict):
        return self._record("sandbox_dispatch_result", {"mission_id": mission_id, "result": result})

    def log_mission(self, request: MissionRequest, result: dict):
        log_data = {
            "mission_id": request.mission_id,
            "requester_id": request.requester_id,
            "chat_id": request.chat_id,
            "action_type": request.action_type,
            "target": request.target,
            "arguments": request.arguments,
            "risk_level": request.risk_level.value,
            "status": request.status.value,
            "result": result,
        }
        return self._record("mission", log_data)
