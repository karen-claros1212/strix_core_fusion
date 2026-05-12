from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from saga_fusion.memory import ContextItem, MemoryRedactor, MemorySensitivity, SessionSummary

from .policy import SessionRecoveryPolicy, neutralize_instruction_text
from .types import CompressedContext


class ContextCompressor:
    def __init__(self, policy: SessionRecoveryPolicy | None = None, redactor: MemoryRedactor | None = None):
        self.policy = policy or SessionRecoveryPolicy()
        self.redactor = redactor or MemoryRedactor()

    def _extract_text(self, item: Any) -> str:
        if isinstance(item, CompressedContext):
            return item.text
        if isinstance(item, SessionSummary):
            return item.text
        if isinstance(item, ContextItem):
            return item.content
        if isinstance(item, dict):
            preferred = item.get("content") or item.get("text") or item.get("summary") or item.get("user_intent")
            return str(preferred if preferred is not None else item)
        if is_dataclass(item):
            # Fast path for the common context dataclass shape.  This preserves
            # the existing precedence while avoiding a full asdict() copy for
            # dataclasses that already expose content/text attributes.
            content = getattr(item, "content", None)
            if content is not None:
                return str(content)
            text = getattr(item, "text", None)
            if text is not None:
                return str(text)
            payload = asdict(item)
            return str(payload.get("content") or payload.get("text") or payload)
        return str(item)

    def compress(self, context: Any, budget_chars: int | None = None) -> CompressedContext:
        budget = max(0, int(self.policy.default_budget_chars if budget_chars is None else budget_chars))
        items = context if isinstance(context, (list, tuple, set)) else (context,)
        rendered: list[str] = []
        rendered_append = rendered.append
        extract_text = self._extract_text
        redact_text = self.redactor.redact_text
        secret_blocked = MemorySensitivity.SECRET_BLOCKED
        neutralize = neutralize_instruction_text
        original_chars = 0
        excluded = 0
        redacted_any = False

        for item in items:
            if item is None:
                continue
            if getattr(item, "sensitivity", None) == secret_blocked:
                excluded += 1
                continue
            text = extract_text(item)
            original_chars += len(text)
            redacted = redact_text(text)
            if redacted.secret_blocked:
                excluded += 1
                redacted_any = True
                # Secret-bearing recovered context is excluded rather than persisted in summaries.
                continue
            inert = neutralize(redacted.text).strip()
            if inert:
                rendered_append(f"[UNTRUSTED_QUOTED_CONTEXT] {inert}")

        joined = "\n".join(rendered)
        truncated = len(joined) > budget
        if truncated:
            suffix = "\n[TRUNCATED_TO_CONTEXT_BUDGET]"
            keep = max(0, budget - len(suffix))
            joined = joined[:keep].rstrip() + suffix if budget else ""
        return CompressedContext(
            text=joined,
            budget_chars=budget,
            original_chars=original_chars,
            compressed_chars=len(joined),
            truncated=truncated,
            redacted=redacted_any,
            excluded_secret_count=excluded,
            non_authoritative=True,
            execution_allowed=False,
        )
