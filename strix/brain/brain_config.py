"""
Brain config loader — reads environment variables without side-effects.

Env vars follow the user-specified naming:
  STRIX_BRAIN_MODE, STRIX_PRIMARY_LLM_PROVIDER, STRIX_FALLBACK_LLM_PROVIDER
  STRIX_LOCAL_LLM_BASE_URL, STRIX_LOCAL_LLM_MODEL, STRIX_LOCAL_LLM_API_KEY
  DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL
  STRIX_LLM_TIMEOUT_SECONDS, STRIX_LLM_MAX_RETRIES, STRIX_LLM_FAIL_CLOSED
"""

from __future__ import annotations

from strix.brain.brain_types import (
    BrainConfig,
    BrainMode,
    BrainProvider,
    _env_int,
    _env_str,
    _parse_mode,
)


def load_brain_config() -> BrainConfig:
    """Read environment and return a BrainConfig.

    No env var is required — every field has a safe default.
    No API keys are printed or logged by this function.
    """
    mode_raw = _env_str("STRIX_BRAIN_MODE", "hybrid")

    return BrainConfig(
        mode=_parse_mode(mode_raw),
        primary_provider=_parse_provider(_env_str("STRIX_PRIMARY_LLM_PROVIDER", "qwen_local")),
        fallback_provider=_parse_provider(_env_str("STRIX_FALLBACK_LLM_PROVIDER", "deepseek")),
        local_base_url=_env_str("STRIX_LOCAL_LLM_BASE_URL", "http://host.docker.internal:8080/v1"),
        local_model=_env_str("STRIX_LOCAL_LLM_MODEL", "qwen3.6-35b-a3b-turboquant"),
        local_api_key=_env_str("STRIX_LOCAL_LLM_API_KEY", "local"),
        deepseek_base_url=_env_str("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        deepseek_model=_env_str("DEEPSEEK_MODEL", "deepseek-v4-flash"),
        deepseek_api_key=_env_str("DEEPSEEK_API_KEY", ""),
        timeout_seconds=_env_int("STRIX_LLM_TIMEOUT_SECONDS", 45),
        max_retries=_env_int("STRIX_LLM_MAX_RETRIES", 1),
        fail_closed=_env_str("STRIX_LLM_FAIL_CLOSED", "true").lower() in {"1", "true", "yes"},
    )


def _parse_provider(raw: str) -> BrainProvider:
    norm = raw.strip().lower().replace("-", "_")
    for p in BrainProvider:
        if p.value == norm:
            return p
    return BrainProvider.qwen_local
