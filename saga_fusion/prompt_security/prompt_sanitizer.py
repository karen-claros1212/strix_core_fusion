from __future__ import annotations

import re

from .prompt_injection_detector import PromptThreatMatch
from .prompt_security_types import SanitizedPrompt, PromptThreatType


class PromptSanitizer:
    def sanitize(self, text: str, matches: list[PromptThreatMatch] | None = None) -> SanitizedPrompt:
        original = text or ''
        normalized = re.sub(r'\s+', ' ', original).strip()
        suspicious = []
        for match in matches or []:
            if match.threat_type != PromptThreatType.BENIGN and match.matched_text:
                suspicious.append(match.matched_text)
        sanitized = normalized
        for segment in suspicious:
            sanitized = sanitized.replace(segment, f'[SUSPICIOUS:{segment}]')
        return SanitizedPrompt(
            original_text=original,
            sanitized_text=sanitized,
            suspicious_segments=suspicious,
            metadata={'normalized_whitespace': normalized != original, 'suspicious_count': len(suspicious)},
        )
