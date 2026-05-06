import hashlib
import re
from typing import List
import time

class TelegramSecurity:
    def __init__(self, config=None, allowed_user_ids: List[int] = None, rate_limit: int = 10):
        if config:
            self.allowed_users = config.allowed_users
        else:
            self.allowed_users = allowed_user_ids or []
        self.rate_limit = rate_limit
        self.seen_hashes = set()
        self.request_times = {}

    def validate_user(self, user_id: str) -> bool:
        return user_id in self.allowed_users

    def redact_secrets(self, text: str) -> str:
        return re.sub(
            r'((?:api[_-]?key|token|password|secret)(?:["\']?)(?:[:=]?)(?:\s*))(\w+)',
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
