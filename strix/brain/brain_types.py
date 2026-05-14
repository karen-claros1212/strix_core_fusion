"""
Brain provider & mode types for STRIX hybrid LLM configuration.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class BrainProvider(Enum):
    qwen_local = "qwen_local"
    deepseek = "deepseek"


class BrainMode(Enum):
    local_first = "local_first"
    hybrid = "hybrid"
    deepseek_only = "deepseek_only"


@dataclass
class BrainConfig:
    mode: BrainMode = BrainMode.local_first
    primary_provider: BrainProvider = BrainProvider.qwen_local
    fallback_provider: BrainProvider = BrainProvider.deepseek

    # Qwen local
    local_base_url: str = ""
    local_model: str = ""
    local_api_key: str = ""

    # DeepSeek
    deepseek_base_url: str = ""
    deepseek_model: str = ""
    deepseek_api_key: str = ""

    # Tuning
    timeout_seconds: int = 120
    max_retries: int = 2
    fail_closed: bool = True

    # Arbitrary metadata (injected into agent config / result metadata)
    extra: dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return (
            f"BrainConfig(mode={self.mode.value}, "
            f"primary={self.primary_provider.value}, "
            f"fallback={self.fallback_provider.value}, "
            f"local_model={self.local_model!r}, "
            f"deepseek_model={self.deepseek_model!r}, "
            f"timeout={self.timeout_seconds}s, "
            f"retries={self.max_retries}, "
            f"fail_closed={self.fail_closed})"
        )

    def redacted_dict(self) -> dict[str, Any]:
        """Serialisable dict with API keys redacted — safe for logs / metadata."""
        return {
            "mode": self.mode.value,
            "primary_provider": self.primary_provider.value,
            "fallback_provider": self.fallback_provider.value,
            "local_base_url": self.local_base_url,
            "local_model": self.local_model,
            "local_api_key": "[REDACTED]" if self.local_api_key else "",
            "deepseek_base_url": self.deepseek_base_url,
            "deepseek_model": self.deepseek_model,
            "deepseek_api_key": "[REDACTED]" if self.deepseek_api_key else "",
            "timeout_seconds": self.timeout_seconds,
            "max_retries": self.max_retries,
            "fail_closed": self.fail_closed,
        }


def _env_str(key: str, default: str = "") -> str:
    return os.environ.get(key, "").strip() or default


def _env_int(key: str, default: int) -> int:
    raw = os.environ.get(key, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except (ValueError, TypeError):
        return default


def _parse_mode(raw: str) -> BrainMode:
    norm = raw.strip().lower().replace("-", "_")
    for m in BrainMode:
        if m.value == norm:
            return m
    return BrainMode.local_first
