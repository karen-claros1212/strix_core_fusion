import re
import time
from typing import List


class TelegramSecurity:
    def __init__(self, config=None, allowed_user_ids: List[int | str] = None, rate_limit: int = 10):
        if config:
            allowed_from_config = getattr(config, "allowed_user_ids", None)
            if not allowed_from_config:
                allowed_from_config = getattr(config, "allowed_users", None)
            self.allowed_users = [str(user).strip() for user in (allowed_from_config or []) if str(user).strip()]
        else:
            self.allowed_users = [str(user).strip() for user in (allowed_user_ids or []) if str(user).strip()]
        self.rate_limit = rate_limit
        self.seen_hashes = set()
        self.request_times = {}

    def validate_user(self, user_id: str | int) -> bool:
        return str(user_id).strip() in self.allowed_users

    def redact_secrets(self, text: str) -> str:
        return re.sub(
            r'((?:api[_-]?key|token|password|secret)(?:["\']?)(?:[:=]?)(?:\s*))([^\s"\']+)',
            r'\1***',
            text,
            flags=re.IGNORECASE,
        )

    def verify_replay(self, action_hash: str) -> bool:
        if action_hash in self.seen_hashes:
            return False
        self.seen_hashes.add(action_hash)
        return True

    def check_rate_limit(self, user_id: str) -> bool:
        now = time.time()
        if user_id not in self.request_times:
            self.request_times[user_id] = []
        self.request_times[user_id] = [t for t in self.request_times[user_id] if now - t < 60]
        if len(self.request_times[user_id]) >= self.rate_limit:
            return False
        self.request_times[user_id].append(now)
        return True
