import hashlib
import re
import time
from typing import Iterable, List


class TelegramSecurity:
    def __init__(self, config=None, allowed_user_ids: List[int | str] = None, rate_limit: int | None = None):
        allowed_from_config = []
        if config:
            allowed_from_config = getattr(config, "allowed_user_ids", None) or getattr(config, "allowed_users", None) or []
        self.allowed_users = self._normalize_users(allowed_from_config if config else (allowed_user_ids or []))
        self.rate_limit = int(rate_limit or getattr(config, "rate_limit_per_minute", 10) or 10)
        self.seen_hashes = set()
        self.request_times = {}

    @staticmethod
    def _normalize_users(values: Iterable[int | str]) -> list[str]:
        return [str(user).strip() for user in values if str(user).strip()]

    def validate_user(self, user_id: str | int) -> bool:
        if not self.allowed_users:
            return False
        return str(user_id).strip() in self.allowed_users

    def redact_secrets(self, text: object) -> str:
        safe = "" if text is None else str(text)
        patterns = [
            (r'(?i)(authorization\s*:\s*bearer\s+)([^\s"\']+)', r'\1[REDACTED]'),
            (r'(?i)((?:telegram[_-]?bot[_-]?token|bot[_-]?token|token|api[_-]?key|secret[_-]?key|password)(?:["\']?)(?:\s*[:=]|\s+)\s*)([^\s"\']+)', r'\1[REDACTED]'),
            (r'\b\d{6,}:[A-Za-z0-9_-]{10,}\b', '[REDACTED]'),
        ]
        for pattern, replacement in patterns:
            safe = re.sub(pattern, replacement, safe)
        return safe

    def action_hash(self, payload: object) -> str:
        redacted = self.redact_secrets(payload)
        return hashlib.sha256(redacted.encode("utf-8")).hexdigest()

    def verify_replay(self, action_hash: str) -> bool:
        if not action_hash:
            return False
        if action_hash in self.seen_hashes:
            return False
        self.seen_hashes.add(action_hash)
        return True

    def check_rate_limit(self, user_id: str | int) -> bool:
        now = time.time()
        key = str(user_id).strip()
        if not key:
            return False
        self.request_times.setdefault(key, [])
        self.request_times[key] = [t for t in self.request_times[key] if now - t < 60]
        if len(self.request_times[key]) >= self.rate_limit:
            return False
        self.request_times[key].append(now)
        return True
