import time

class RateLimiter:
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}  # user_id -> list of timestamps

    def is_allowed(self, user_id: str) -> bool:
        """Check if user is within rate limits."""
        now = time.time()
        if user_id not in self.requests:
            self.requests[user_id] = []
        
        # Remove old timestamps
        self.requests[user_id] = [t for t in self.requests[user_id] if now - t < self.window_seconds]
        
        if len(self.requests[user_id]) >= self.max_requests:
            return False
        
        self.requests[user_id].append(now)
        return True
