import os
from dataclasses import dataclass, field


def _parse_allowed_user_ids(raw_value: str | None) -> list[str]:
    if not raw_value:
        return []
    return [item.strip() for item in raw_value.split(",") if item.strip()]


@dataclass
class TelegramConfig:
    bot_token: str = field(default_factory=lambda: os.environ.get("TELEGRAM_BOT_TOKEN", "").strip())
    allowed_user_ids: list[str] = field(
        default_factory=lambda: _parse_allowed_user_ids(os.environ.get("TELEGRAM_ALLOWED_USER_IDS"))
    )
    default_risk_threshold: str = "R4"
    approval_timeout_minutes: int = 30
    is_ready: bool = field(init=False)
    allowed_users: list[str] = field(init=False)

    def __post_init__(self):
        self.allowed_user_ids = [str(item).strip() for item in (self.allowed_user_ids or []) if str(item).strip()]
        self.is_ready = bool(self.bot_token and self.allowed_user_ids)
        self.allowed_users = list(self.allowed_user_ids) if self.allowed_user_ids else ["diego_claros", "admin"]

    @property
    def config_error(self) -> str:
        missing = []
        if not self.bot_token:
            missing.append("TELEGRAM_BOT_TOKEN")
        if not self.allowed_user_ids:
            missing.append("TELEGRAM_ALLOWED_USER_IDS")
        if not missing:
            return ""
        return f"Telegram real mode disabled: missing {', '.join(missing)}."
