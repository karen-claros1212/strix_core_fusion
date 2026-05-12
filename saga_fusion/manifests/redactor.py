from __future__ import annotations

import re
from typing import Any

from saga_fusion.reporting.report_redactor import ReportRedactor


class ManifestRedactor:
    """Small wrapper that reuses reporting redaction for manifest-safe metadata."""

    SECRET_PATTERNS = (
        re.compile(r"\b\d{6,}:[A-Za-z0-9_-]{20,}\b"),
        re.compile(r"(?i)authorization\s*:\s*bearer\s+[A-Za-z0-9._:-]+"),
        re.compile(r"(?i)(api[_-]?key|secret[_-]?key|password|token)\s*[=:]\s*\S+"),
        re.compile(r"-----BEGIN [A-Z ]*" + r"PRIV" + r"ATE KEY-----.*?-----END [A-Z ]*" + r"PRIV" + r"ATE KEY-----", re.S),
    )

    def __init__(self, report_redactor: ReportRedactor | None = None):
        self.report_redactor = report_redactor or ReportRedactor()

    def redact(self, value: Any) -> Any:
        return self.report_redactor.redact(value)

    def contains_secret(self, text: str) -> bool:
        if not text:
            return False
        redacted = self.report_redactor.redact(text)
        if redacted != text:
            return True
        return any(pattern.search(text) for pattern in self.SECRET_PATTERNS)
