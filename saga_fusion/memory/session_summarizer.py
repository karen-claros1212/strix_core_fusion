from __future__ import annotations

from typing import Any

from .memory_redactor import MemoryRedactor
from .memory_types import SessionSummary, MemorySensitivity


class SessionSummarizer:
    def __init__(self, redactor: MemoryRedactor | None = None, max_items: int = 6):
        self.redactor = redactor or MemoryRedactor()
        self.max_items = max_items

    def summarize(self, events: list[dict[str, Any]] | tuple[dict[str, Any], ...]) -> SessionSummary:
        decisions: list[str] = []
        risks: list[str] = []
        approvals: list[str] = []
        evidence: list[str] = []
        followups: list[str] = []
        blocked = False
        for event in events or []:
            kind = str(event.get("type") or event.get("event") or "event")
            if event.get("decision") or "policy" in kind:
                decisions.append(f"{kind}: {event.get('decision') or event.get('reason') or event.get('status')}")
            if event.get("risk_level"):
                risks.append(str(event.get("risk_level")))
            if event.get("approval_id") or "approval" in kind:
                approvals.append(f"{event.get('approval_id', 'approval')}: {event.get('status', event.get('decision', 'recorded'))}")
            for key in ("evidence_ref", "evidence_refs"):
                val = event.get(key)
                if isinstance(val, str):
                    evidence.append(val)
                elif isinstance(val, (list, tuple)):
                    evidence.extend(str(v) for v in val)
            if event.get("next_step") or event.get("follow_up"):
                followups.append(str(event.get("next_step") or event.get("follow_up")))
        text_parts = []
        if decisions:
            text_parts.append("Decisions: " + "; ".join(decisions[: self.max_items]))
        if risks:
            text_parts.append("Risks: " + ", ".join(list(dict.fromkeys(risks))[: self.max_items]))
        if approvals:
            text_parts.append("Approvals: " + "; ".join(approvals[: self.max_items]))
        if evidence:
            text_parts.append("Evidence: " + ", ".join(list(dict.fromkeys(evidence))[: self.max_items]))
        if followups:
            text_parts.append("Follow-ups: " + "; ".join(followups[: self.max_items]))
        text = " | ".join(text_parts) or "No durable mission decisions recorded."
        redacted = self.redactor.redact_text(text)
        blocked = redacted.secret_blocked
        return SessionSummary(
            decisions=tuple(self.redactor.redact_text(x).text for x in decisions[: self.max_items]),
            risks=tuple(dict.fromkeys(risks)),
            approvals=tuple(self.redactor.redact_text(x).text for x in approvals[: self.max_items]),
            evidence_refs=tuple(dict.fromkeys(self.redactor.redact_text(x).text for x in evidence[: self.max_items])),
            follow_ups=tuple(self.redactor.redact_text(x).text for x in followups[: self.max_items]),
            text=redacted.text,
            sensitivity=MemorySensitivity.SECRET_BLOCKED if blocked else MemorySensitivity.INTERNAL,
        )
