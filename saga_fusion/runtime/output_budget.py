import re
from typing import Optional, Tuple
from saga_fusion.audit_logger import SagaAuditLogger

class SagaOutputBudget:
    def __init__(self, evidence_store=None, max_chars: int = 12000, preserve_head: int = 4000, preserve_tail: int = 8000):
        self.evidence_store = evidence_store
        self.max_chars = max_chars
        self.preserve_head = preserve_head
        self.preserve_tail = preserve_tail
        self.logger = SagaAuditLogger()

    def truncate_output(self, text: str) -> str:
        if len(text) <= self.max_chars:
            return text
        
        head = text[:self.preserve_head]
        tail = text[-self.preserve_tail:] if len(text) > self.preserve_tail else ""
        truncated_text = f"{head}\n[TRUNCATED: Output exceeded {self.max_chars} chars]\n{tail}"
        return truncated_text

    def split_raw_and_model_view(self, text: str, mission_id: str, artifact_name: str) -> Tuple[str, str]:
        model_view = self.truncate_output(text)
        model_view = self.logger.redact_secrets(model_view)
        
        if self.evidence_store:
            self.evidence_store.write_raw_output(mission_id, artifact_name, text)
            
        return text, model_view
