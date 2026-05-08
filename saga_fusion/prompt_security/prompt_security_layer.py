from __future__ import annotations

from .prompt_injection_detector import PromptInjectionDetector
from .prompt_policy import PromptPolicy
from .prompt_sanitizer import PromptSanitizer


class PromptSecurityLayer:
    def __init__(self, detector: PromptInjectionDetector | None = None, sanitizer: PromptSanitizer | None = None, policy: PromptPolicy | None = None):
        self.detector = detector or PromptInjectionDetector()
        self.sanitizer = sanitizer or PromptSanitizer()
        self.policy = policy or PromptPolicy()

    def evaluate(self, text: str, context=None):
        matches = self.detector.detect(text)
        return self.policy.decide(text, matches, context=context)

    def sanitize(self, text: str, context=None):
        matches = self.detector.detect(text)
        return self.sanitizer.sanitize(text, matches)

    def guard_for_llm(self, text: str, context=None) -> dict:
        matches = self.detector.detect(text)
        decision = self.policy.decide(text, matches, context=context)
        sanitized = self.sanitizer.sanitize(text, matches)
        return {
            'decision': decision,
            'sanitized': sanitized,
            'safe_to_call_llm': decision.safe_to_call_llm,
            'risk_level': decision.risk_level.value,
            'threats': [threat.value for threat in decision.threats],
            'reason': decision.reason,
            'matched_patterns': decision.matched_patterns,
        }
