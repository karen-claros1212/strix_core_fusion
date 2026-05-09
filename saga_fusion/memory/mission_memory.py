from __future__ import annotations

from .memory_redactor import MemoryRedactor
from .memory_store import MemoryStore
from .memory_types import MemoryRecord, MissionMemoryRecord, MemoryScope, MemorySensitivity


class MissionMemory:
    def __init__(self, store: MemoryStore | None = None, redactor: MemoryRedactor | None = None):
        self.redactor = redactor or MemoryRedactor()
        self.store = store or MemoryStore(self.redactor)

    def remember(
        self,
        *,
        mission_id: str,
        user_intent: str,
        policy_decision: str,
        risk_level: str,
        approval_status: str = "not_required",
        evidence_refs: list[str] | tuple[str, ...] = (),
        report_refs: list[str] | tuple[str, ...] = (),
        outcome: str = "pending",
        next_step: str = "",
    ) -> MemoryRecord:
        record = MissionMemoryRecord(
            mission_id=str(mission_id),
            user_intent=self.redactor.redact_text(user_intent).text,
            policy_decision=self.redactor.redact_text(policy_decision).text,
            risk_level=str(risk_level),
            approval_status=self.redactor.redact_text(approval_status).text,
            evidence_refs=tuple(self.redactor.redact_text(str(x)).text for x in evidence_refs),
            report_refs=tuple(self.redactor.redact_text(str(x)).text for x in report_refs),
            outcome=self.redactor.redact_text(outcome).text,
            next_step=self.redactor.redact_text(next_step).text,
        )
        return self.store.add(record.to_memory_record())

    def from_plan(self, mission_id: str, user_intent: str, policy_decision: str, risk_level: str, evidence_ref: str = "", next_step: str = "") -> MemoryRecord:
        return self.remember(
            mission_id=mission_id,
            user_intent=user_intent,
            policy_decision=policy_decision,
            risk_level=risk_level,
            approval_status="pending" if str(risk_level) == "R4" else "not_required",
            evidence_refs=tuple([evidence_ref] if evidence_ref else []),
            outcome="planned",
            next_step=next_step,
        )

    def from_report(self, mission_id: str, user_intent: str, risk_level: str, report_ref: str, outcome: str, next_step: str = "") -> MemoryRecord:
        return self.remember(
            mission_id=mission_id,
            user_intent=user_intent,
            policy_decision="report_generated",
            risk_level=risk_level,
            report_refs=(report_ref,) if report_ref else (),
            outcome=outcome,
            next_step=next_step,
        )

    def list_for_mission(self, mission_id: str) -> list[MemoryRecord]:
        return self.store.list_by_mission(mission_id)
