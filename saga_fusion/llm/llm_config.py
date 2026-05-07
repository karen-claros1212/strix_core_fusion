import os
from dataclasses import dataclass, field


def _env_bool(name: str, default: bool = False) -> bool:
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


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    try:
        return float(raw)
    except ValueError:
        return default


@dataclass
class LLMConfig:
    provider: str = field(default_factory=lambda: os.environ.get("STRIX_LLM_PROVIDER", "openai_compatible").strip())
    base_url: str = field(default_factory=lambda: os.environ.get("STRIX_LLM_BASE_URL", "").strip().rstrip("/"))
    model: str = field(default_factory=lambda: os.environ.get("STRIX_LLM_MODEL", "").strip())
    api_key: str = field(default_factory=lambda: os.environ.get("STRIX_LLM_API_KEY", "").strip())
    timeout_seconds: int = field(default_factory=lambda: _env_int("STRIX_LLM_TIMEOUT_SECONDS", 120))
    max_output_tokens: int = field(default_factory=lambda: _env_int("STRIX_LLM_MAX_OUTPUT_TOKENS", 2048))
    temperature: float = field(default_factory=lambda: _env_float("STRIX_LLM_TEMPERATURE", 0.2))
    enabled: bool = field(default_factory=lambda: _env_bool("STRIX_LLM_ENABLED", False))

    def redacted_repr(self) -> str:
        return redacted_repr(self)

    def __repr__(self) -> str:
        return self.redacted_repr()


def load_llm_config() -> LLMConfig:
    return LLMConfig()


def validate_llm_config(config: LLMConfig | None = None) -> tuple[bool, list[str]]:
    cfg = config or load_llm_config()
    missing: list[str] = []
    if not cfg.enabled:
        return True, missing
    if not cfg.base_url:
        missing.append("STRIX_LLM_BASE_URL")
    if not cfg.model:
        missing.append("STRIX_LLM_MODEL")
    return not missing, missing


def redacted_repr(config: LLMConfig) -> str:
    api_key = "[REDACTED]" if config.api_key and config.api_key != "local" else config.api_key
    return (
        "LLMConfig("
        f"provider={config.provider!r}, "
        f"base_url={config.base_url!r}, "
        f"model={config.model!r}, "
        f"api_key={api_key!r}, "
        f"timeout_seconds={config.timeout_seconds!r}, "
        f"max_output_tokens={config.max_output_tokens!r}, "
        f"temperature={config.temperature!r}, "
        f"enabled={config.enabled!r})"
    )
