import os
from dataclasses import dataclass, field
from typing import Iterable


VALID_TELEGRAM_MODES = {"mock", "real"}


def _parse_allowed_user_ids(raw_value: str | Iterable[str] | None) -> list[str]:
    if raw_value is None:
        return []
    if isinstance(raw_value, str):
        parts = raw_value.split(",")
    else:
        parts = list(raw_value)
    return [str(item).strip() for item in parts if str(item).strip()]


def _env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    try:
        value = int(raw)
    except ValueError:
        return default
    return value if value > 0 else default


@dataclass
class TelegramConfig:
    bot_token: str = field(default_factory=lambda: os.environ.get("TELEGRAM_BOT_TOKEN", "").strip())
    allowed_user_ids: list[str] = field(
        default_factory=lambda: _parse_allowed_user_ids(os.environ.get("TELEGRAM_ALLOWED_USER_IDS"))
    )
    mode: str = field(default_factory=lambda: os.environ.get("TELEGRAM_MODE", "mock").strip().lower() or "mock")
    polling_enabled: bool = field(default_factory=lambda: _env_bool("TELEGRAM_POLLING_ENABLED", True))
    webhook_enabled: bool = field(default_factory=lambda: _env_bool("TELEGRAM_WEBHOOK_ENABLED", False))
    rate_limit_per_minute: int = field(default_factory=lambda: _env_int("TELEGRAM_RATE_LIMIT_PER_MINUTE", 10))
    default_risk_threshold: str = "R4"
    approval_timeout_minutes: int = 30
    is_ready: bool = field(init=False)
    allowed_users: list[str] = field(init=False)

    def __post_init__(self):
        self.mode = (self.mode or "mock").strip().lower()
        if self.mode not in VALID_TELEGRAM_MODES:
            self.mode = "mock"
        self.allowed_user_ids = _parse_allowed_user_ids(self.allowed_user_ids)
        self.allowed_users = list(self.allowed_user_ids)
        self.bot_token = (self.bot_token or "").strip()
        self.is_ready = self.mode == "mock" or validate_real_mode_config(self)[0]

    @property
    def config_error(self) -> str:
        ok, errors = validate_real_mode_config(self)
        if ok:
            return ""
        return f"Telegram real mode disabled: missing {', '.join(errors)}."

    @property
    def redacted_bot_token(self) -> str:
        return "[REDACTED]" if self.bot_token else ""

    def __repr__(self) -> str:
        return (
            "TelegramConfig("
            f"mode={self.mode!r}, "
            f"bot_token={self.redacted_bot_token!r}, "
            f"allowed_user_ids={self.allowed_user_ids!r}, "
            f"polling_enabled={self.polling_enabled!r}, "
            f"webhook_enabled={self.webhook_enabled!r}, "
            f"rate_limit_per_minute={self.rate_limit_per_minute!r})"
        )


def load_telegram_config() -> TelegramConfig:
    return TelegramConfig()


def validate_real_mode_config(config: TelegramConfig | None = None) -> tuple[bool, list[str]]:
    cfg = config or load_telegram_config()
    missing: list[str] = []
    if not getattr(cfg, "bot_token", ""):
        missing.append("TELEGRAM_BOT_TOKEN")
    if not getattr(cfg, "allowed_user_ids", []):
        missing.append("TELEGRAM_ALLOWED_USER_IDS")
    return not missing, missing
