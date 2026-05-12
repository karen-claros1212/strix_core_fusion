from __future__ import annotations

from .error_classifier import LLMErrorClassifier
from .error_types import LLMErrorRecord, LLMRecoveryDecision
from .recovery_policy import LLMRecoveryPolicy


class LLMRecoveryManager:
    def __init__(self, policy: LLMRecoveryPolicy | None = None, classifier: LLMErrorClassifier | None = None):
        self.policy = policy or LLMRecoveryPolicy()
        self.classifier = classifier or LLMErrorClassifier()
        self.last_error: LLMErrorRecord | None = None
        self.last_decision: LLMRecoveryDecision | None = None
        self.history: list[dict] = []

    def decide(self, record: LLMErrorRecord) -> LLMRecoveryDecision:
        decision = self.policy.decide(record)
        self.last_error = record
        self.last_decision = decision
        self.history.append({"error": record.to_dict(), "decision": decision.to_dict()})
        return decision

    def run_chat_completion(self, client, messages, *, config=None):
        """Call a provided client with explicit bounded retries; never sleeps or executes tools."""
        max_attempts = max(self.policy.max_retry_count, 0) + 1
        attempt = 0
        while attempt < max_attempts:
            try:
                response = client.chat_completion(messages)
            except Exception as exc:
                record = self.classifier.classify_exception(exc, config=config, retry_count=attempt)
                decision = self.decide(record)
                if decision.should_retry:
                    attempt += 1
                    continue
                return None, record, decision
            record = self.classifier.classify_response(response, config=config, retry_count=attempt)
            if record is None:
                return response, None, None
            decision = self.decide(record)
            if decision.should_retry:
                attempt += 1
                continue
            return response, record, decision
        return None, self.last_error, self.last_decision

    def recovery_metadata(self) -> dict:
        return {
            "last_error": self.last_error.to_dict() if self.last_error else None,
            "last_decision": self.last_decision.to_dict() if self.last_decision else None,
            "history": list(self.history),
        }
