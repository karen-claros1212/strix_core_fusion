from __future__ import annotations

import re
from datetime import datetime


class ApprovalAudit:
    def __init__(self):
        self.records = []

    def record(self, event_type: str, data: dict):
        redacted = self._redact(data)
        redacted['event_type'] = event_type
        redacted['timestamp'] = datetime.utcnow().isoformat()
        self.records.append(redacted)
        return redacted

    def _redact(self, value):
        if isinstance(value, dict):
            return {k: self._redact(v) for k, v in value.items()}
        if isinstance(value, list):
            return [self._redact(v) for v in value]
        if isinstance(value, str):
            value = re.sub(r'ghp_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+', '[REDACTED]', value)
            value = re.sub(r'\b\d{6,}:[A-Za-z0-9_-]{20,}\b', '[REDACTED]', value)
            value = re.sub(r'(?i)((api[_-]?key|secret[_-]?key|password|token)\s*=\s*)[^\s]+', r'\1[REDACTED]', value)
        return value
