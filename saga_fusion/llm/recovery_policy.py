from __future__ import annotations

from dataclasses import dataclass, field

from .error_types import LLMErrorCategory, LLMRecoveryDecision


@dataclass(frozen=True)
class LLMRecoveryPolicy:
    max_retry_count: int = 2
    category_retry_limits: dict[LLMErrorCategory, int] = field(default_factory=lambda: {
        LLMErrorCategory.TIMEOUT: 2,
        LLMErrorCategory.CONNECTION: 2,
        LLMErrorCategory.RATE_LIMIT: 2,
        LLMErrorCategory.SERVER_ERROR: 1,
    })
    base_backoff_seconds: float = 0.25

    def decide(self, record) -> LLMRecoveryDecision:
        limit = min(self.category_retry_limits.get(record.category, 0), self.max_retry_count)
        should_retry = bool(record.retryable and record.retry_count < limit)
        backoff = round(self.base_backoff_seconds * (2 ** max(record.retry_count, 0)), 3) if should_retry else None
        reason = "retry_with_bounded_backoff_metadata" if should_retry else "safe_fallback_non_executing_router"
        if record.category in {LLMErrorCategory.AUTH, LLMErrorCategory.UNSAFE_OUTPUT, LLMErrorCategory.CONTEXT_TOO_LARGE, LLMErrorCategory.INVALID_RESPONSE, LLMErrorCategory.MODEL_UNAVAILABLE}:
            reason = f"nonretryable_{record.category.value}_safe_fallback"
        elif record.retryable and not should_retry:
            reason = "max_retries_exceeded_safe_fallback"
        return LLMRecoveryDecision(
            should_retry=should_retry,
            fallback_to_safe_router=not should_retry,
            reason=reason,
            max_retry_count=limit,
            retry_count=record.retry_count,
            backoff_seconds=backoff,
            category=record.category,
            metadata={"retryable": record.retryable, "severity": record.severity.value},
        )
