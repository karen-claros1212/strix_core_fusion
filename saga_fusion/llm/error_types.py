from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class LLMErrorCategory(str, Enum):
    AUTH = "auth"
    TIMEOUT = "timeout"
    CONNECTION = "connection"
    RATE_LIMIT = "rate_limit"
    SERVER_ERROR = "server_error"
    INVALID_RESPONSE = "invalid_response"
    UNSAFE_OUTPUT = "unsafe_output"
    CONTEXT_TOO_LARGE = "context_too_large"
    MODEL_UNAVAILABLE = "model_unavailable"
    UNKNOWN = "unknown"


class LLMErrorSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass(frozen=True)
class LLMErrorRecord:
    category: LLMErrorCategory
    severity: LLMErrorSeverity
    message: str
    retryable: bool
    status_code: int | None = None
    provider: str = ""
    model: str = ""
    operation: str = "chat_completion"
    retry_count: int = 0
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "category": self.category.value,
            "severity": self.severity.value,
            "message": self.message,
            "retryable": self.retryable,
            "status_code": self.status_code,
            "provider": self.provider,
            "model": self.model,
            "operation": self.operation,
            "retry_count": self.retry_count,
            "details": self.details,
        }


@dataclass(frozen=True)
class LLMRecoveryDecision:
    should_retry: bool
    fallback_to_safe_router: bool
    reason: str
    max_retry_count: int
    retry_count: int = 0
    backoff_seconds: float | None = None
    category: LLMErrorCategory = LLMErrorCategory.UNKNOWN
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "should_retry": self.should_retry,
            "fallback_to_safe_router": self.fallback_to_safe_router,
            "reason": self.reason,
            "max_retry_count": self.max_retry_count,
            "retry_count": self.retry_count,
            "backoff_seconds": self.backoff_seconds,
            "category": self.category.value,
            "metadata": self.metadata,
        }
