from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import re
from typing import Any

from .memory_types import MemorySensitivity


@dataclass(frozen=True)
class RedactionResult:
    text: str
    sensitivity: MemorySensitivity
    secret_blocked: bool = False
    fingerprints: tuple[str, ...] = ()
    reasons: tuple[str, ...] = field(default_factory=tuple)


class MemoryRedactor:
    """Memory-specific redactor. Real secrets are replaced before persistence."""

    PRIVATE_KEY_RE = re.compile(r"-----BEGIN [A-Z0-9 ]*" + r"PRIV" + r"ATE KEY-----.*?-----END [A-Z0-9 ]*" + r"PRIV" + r"ATE KEY-----", re.S)
    TELEGRAM_TOKEN_RE = re.compile(r"\b\d{6,}:[A-Za-z0-9_-]{20,}\b")
    AUTH_RE = re.compile(r"(?i)(Authorization\s*[:=]\s*(?:Bearer|Basic)?\s*)[^\s,;]+")
    ASSIGNMENT_RE = re.compile(
        r"(?i)\b(TELEGRAM_BOT_TOKEN|STRIX_LLM_API_KEY|[A-Z0-9_]*(?:API[_-]?KEY|TOKEN|SECRET|PASSWORD)[A-Z0-9_]*)\s*[:=]\s*([^\s'\"`]+)"
    )
    COOKIE_RE = re.compile(r"(?i)\b(cookie|set-cookie)\s*[:=]\s*[^\n;]+(?:;[^\n]*)?")
    PASSWORD_RE = re.compile(r"(?i)\b(password|passwd|pwd)\s*[:=]\s*([^\s'\"`]+)")
    GENERIC_TOKEN_RE = re.compile(r"(?i)\b(token|secret|api[_-]?key)\s*[:=]\s*([A-Za-z0-9._\-:/+=]{8,})")
    ENV_PATH_RE = re.compile(r"(?i)(?:^|\s)(?:[\w./-]*\.env(?:\.\w+)?|~/\.ssh(?:/[^\s]*)?|/home/[^\s]+/\.ssh(?:/[^\s]*)?)")
    ENV_LINE_RE = re.compile(r"(?m)^\s*[A-Z][A-Z0-9_]{2,}\s*=\s*.+$")

    SAFE_REPLACEMENT = "[REDACTED_SECRET]"

    def fingerprint(self, value: str) -> str:
        return "sha256:" + hashlib.sha256(value.encode("utf-8", errors="ignore")).hexdigest()[:16]

    def _redact_match_value(self, match: re.Match, value_group: int, label: str, fps: list[str], reasons: list[str]) -> str:
        value = match.group(value_group)
        if value:
            fps.append(self.fingerprint(value))
        reasons.append(label)
        start, end = match.span(value_group)
        return match.group(0)[: start - match.start()] + self.SAFE_REPLACEMENT + match.group(0)[end - match.start():]

    def redact_text(self, text: str | None) -> RedactionResult:
        source = "" if text is None else str(text)
        fingerprints: list[str] = []
        reasons: list[str] = []
        blocked = False

        def block_whole(match: re.Match, label: str) -> str:
            nonlocal blocked
            blocked = True
            secret = match.group(0)
            fingerprints.append(self.fingerprint(secret))
            reasons.append(label)
            return f"[REDACTED_{label.upper()}]"

        redacted = self.PRIVATE_KEY_RE.sub(lambda m: block_whole(m, "private_key"), source)
        redacted = self.TELEGRAM_TOKEN_RE.sub(lambda m: block_whole(m, "telegram_token"), redacted)

        def assignment_repl(m: re.Match) -> str:
            nonlocal blocked
            blocked = True
            key = m.group(1)
            val = m.group(2)
            fingerprints.append(self.fingerprint(val))
            reasons.append(key.lower())
            return f"{key}={self.SAFE_REPLACEMENT}"

        redacted = self.ASSIGNMENT_RE.sub(assignment_repl, redacted)

        def auth_repl(m: re.Match) -> str:
            nonlocal blocked
            blocked = True
            fingerprints.append(self.fingerprint(m.group(0)))
            reasons.append("authorization")
            return m.group(1) + self.SAFE_REPLACEMENT

        redacted = self.AUTH_RE.sub(auth_repl, redacted)
        redacted = self.COOKIE_RE.sub(lambda m: block_whole(m, "cookie"), redacted)
        redacted = self.PASSWORD_RE.sub(lambda m: self._password_repl(m, fingerprints, reasons), redacted)
        if self.PASSWORD_RE.search(source):
            blocked = True
        redacted = self.GENERIC_TOKEN_RE.sub(lambda m: self._generic_repl(m, fingerprints, reasons), redacted)
        if self.GENERIC_TOKEN_RE.search(source):
            blocked = True
        redacted = self.ENV_PATH_RE.sub(lambda m: block_whole(m, "secret_path"), redacted)

        # Treat pasted .env style lines as blocked even when key name is unknown.
        if ".env" in source.lower():
            blocked = True
            reasons.append("env_reference")
        for env_line in self.ENV_LINE_RE.findall(source):
            if any(word in env_line.upper() for word in ("KEY", "TOKEN", "SECRET", "PASSWORD")):
                blocked = True
                reasons.append("env_secret_line")

        sensitivity = MemorySensitivity.SECRET_BLOCKED if blocked else MemorySensitivity.INTERNAL
        return RedactionResult(redacted, sensitivity, blocked, tuple(dict.fromkeys(fingerprints)), tuple(dict.fromkeys(reasons)))

    def _password_repl(self, m: re.Match, fingerprints: list[str], reasons: list[str]) -> str:
        fingerprints.append(self.fingerprint(m.group(2)))
        reasons.append(m.group(1).lower())
        return f"{m.group(1)}={self.SAFE_REPLACEMENT}"

    def _generic_repl(self, m: re.Match, fingerprints: list[str], reasons: list[str]) -> str:
        fingerprints.append(self.fingerprint(m.group(2)))
        reasons.append(m.group(1).lower())
        return f"{m.group(1)}={self.SAFE_REPLACEMENT}"

    def redact(self, value: Any) -> Any:
        if isinstance(value, dict):
            return {k: self.redact(v) for k, v in value.items()}
        if isinstance(value, (list, tuple, set)):
            return [self.redact(v) for v in value]
        if isinstance(value, str):
            return self.redact_text(value).text
        return value
