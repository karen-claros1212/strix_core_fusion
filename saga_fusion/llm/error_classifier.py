from __future__ import annotations

import re
from typing import Any

from .error_types import LLMErrorCategory, LLMErrorRecord, LLMErrorSeverity

_SECRET_PATTERNS = [
    (re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]+"), "bearer"),
    (re.compile(r"(?i)(api[_-]?key|token|secret|authorization)(\s*[:=]\s*)(['\"]?)[^\s,'\"}]+"), "assignment"),
    (re.compile(r"\bsk-[A-Za-z0-9][A-Za-z0-9_-]{8,}\b"), "openai_key"),
]

_CONTEXT_PATTERNS = (
    "context length", "context_length", "maximum context", "max context", "too many tokens",
    "token limit", "context window", "context too large", "prompt is too long",
)

_UNSAFE_OUTPUT_PATTERNS = (
    "bypass missionpolicy", "ignore missionpolicy", "skip approval", "bypass approval",
    "disable sandbox", "bypass sandbox", "execute tool", "run tool", "call tool",
    "use the shell", "without approval", "ignore promptsecurity",
)


def redact_llm_evidence(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): redact_llm_evidence(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [redact_llm_evidence(v) for v in value]
    text = "" if value is None else str(value)
    for pattern, kind in _SECRET_PATTERNS:
        if kind == "bearer":
            text = pattern.sub("Bearer [REDACTED]", text)
        elif kind == "openai_key":
            text = pattern.sub("sk-[REDACTED]", text)
        else:
            text = pattern.sub(lambda m: f"{m.group(1)}{m.group(2)}{m.group(3)}[REDACTED]", text)
    return text


class LLMErrorClassifier:
    def classify_response(self, response, *, config=None, operation: str = "chat_completion", retry_count: int = 0) -> LLMErrorRecord | None:
        if response is None:
            return self._record(LLMErrorCategory.UNKNOWN, "missing_llm_response", config=config, operation=operation, retry_count=retry_count)
        if getattr(response, "ok", False):
            return None
        status_code = getattr(response, "status_code", None)
        raw_error = getattr(response, "error", "") or "unknown"
        raw = getattr(response, "raw", None)
        return self.classify_error(raw_error, status_code=status_code, config=config, operation=operation, retry_count=retry_count, details={"raw": raw} if raw else {})

    def classify_exception(self, exc: Exception, *, config=None, operation: str = "chat_completion", retry_count: int = 0) -> LLMErrorRecord:
        name = type(exc).__name__
        message = f"{name}: {exc}"
        return self.classify_error(message, config=config, operation=operation, retry_count=retry_count, details={"exception_type": name})

    def classify_error(self, error: object, *, status_code: int | None = None, config=None, operation: str = "chat_completion", retry_count: int = 0, details: dict[str, Any] | None = None) -> LLMErrorRecord:
        safe_message = redact_llm_evidence(error or "unknown")
        lowered = str(safe_message).lower()
        category = LLMErrorCategory.UNKNOWN
        if status_code in {401, 403} or any(term in lowered for term in ("auth", "unauthorized", "forbidden", "invalid api key", "permission")):
            category = LLMErrorCategory.AUTH
        elif status_code == 429 or "rate limit" in lowered or "too many requests" in lowered:
            category = LLMErrorCategory.RATE_LIMIT
        elif status_code in {408, 504} or "timeout" in lowered or "timed out" in lowered:
            category = LLMErrorCategory.TIMEOUT
        elif status_code == 404 or "model not found" in lowered or "model unavailable" in lowered:
            category = LLMErrorCategory.MODEL_UNAVAILABLE
        elif any(term in lowered for term in _CONTEXT_PATTERNS):
            category = LLMErrorCategory.CONTEXT_TOO_LARGE
        elif status_code is not None and 500 <= status_code <= 599:
            category = LLMErrorCategory.SERVER_ERROR
        elif "connection" in lowered or "endpoint_unavailable" in lowered or "transport_error" in lowered or "urlerror" in lowered:
            category = LLMErrorCategory.CONNECTION
        elif "invalid" in lowered or "empty_response" in lowered or "json" in lowered:
            category = LLMErrorCategory.INVALID_RESPONSE
        return self._record(category, str(safe_message), status_code=status_code, config=config, operation=operation, retry_count=retry_count, details=details)

    def classify_invalid_response(self, content: object, *, config=None, operation: str = "parse_mission", retry_count: int = 0) -> LLMErrorRecord:
        return self._record(LLMErrorCategory.INVALID_RESPONSE, "invalid_or_unparseable_llm_response", config=config, operation=operation, retry_count=retry_count, details={"content_preview": redact_llm_evidence(str(content)[:240])})

    def classify_unsafe_output(self, content: object, *, config=None, operation: str = "parse_mission", retry_count: int = 0, reason: str = "unsafe_llm_output") -> LLMErrorRecord:
        return self._record(LLMErrorCategory.UNSAFE_OUTPUT, reason, config=config, operation=operation, retry_count=retry_count, details={"content_preview": redact_llm_evidence(str(content)[:240])})

    def output_looks_unsafe(self, content: object) -> bool:
        lowered = str(content or "").lower()
        return any(pattern in lowered for pattern in _UNSAFE_OUTPUT_PATTERNS)

    def _record(self, category: LLMErrorCategory, message: str, *, status_code: int | None = None, config=None, operation: str, retry_count: int, details: dict[str, Any] | None = None) -> LLMErrorRecord:
        severity = LLMErrorSeverity.ERROR
        if category in {LLMErrorCategory.AUTH, LLMErrorCategory.UNSAFE_OUTPUT}:
            severity = LLMErrorSeverity.CRITICAL
        elif category in {LLMErrorCategory.TIMEOUT, LLMErrorCategory.RATE_LIMIT, LLMErrorCategory.CONNECTION, LLMErrorCategory.SERVER_ERROR}:
            severity = LLMErrorSeverity.WARNING
        retryable = category in {LLMErrorCategory.TIMEOUT, LLMErrorCategory.CONNECTION, LLMErrorCategory.RATE_LIMIT, LLMErrorCategory.SERVER_ERROR}
        return LLMErrorRecord(
            category=category,
            severity=severity,
            message=str(redact_llm_evidence(message)),
            retryable=retryable,
            status_code=status_code,
            provider=str(getattr(config, "provider", "") or ""),
            model=str(getattr(config, "model", "") or ""),
            operation=operation,
            retry_count=retry_count,
            details=redact_llm_evidence(details or {}),
        )
