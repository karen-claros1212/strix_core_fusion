from dataclasses import dataclass
from typing import List

@dataclass
class TelegramConfig:
    bot_token: str = "mock_token"
    allowed_users: List[str] = None
    default_risk_threshold: str = "R4"
    approval_timeout_minutes: int = 30

    def __post_init__(self):
        if self.allowed_users is None:
            self.allowed_users = ["diego_claros", "admin"]
