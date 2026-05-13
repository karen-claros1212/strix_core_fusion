from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .credential_theft_workflow import run_credential_theft_workflow
from .defense_status_workflow import run_defense_status_workflow
from .defensive_workflow_types import DefensiveWorkflowKind, DefensiveWorkflowPlan
from .malware_triage_workflow import run_malware_triage_workflow
from .phishing_attachment_workflow import run_phishing_attachment_workflow
from .ransomware_response_workflow import run_ransomware_response_workflow
from .suspicious_process_workflow import run_suspicious_process_workflow
from .webshell_investigation_workflow import run_webshell_investigation_workflow


@dataclass(frozen=True)
class DefensiveWorkflowDefinition:
    workflow_id: str
    name: str
    runner: Callable[..., DefensiveWorkflowPlan]
    execution_allowed: bool = False
    report_required: bool = True
    evidence_required: bool = True
    non_authoritative: bool = True

    def run(self, **kwargs) -> DefensiveWorkflowPlan:
        plan = self.runner(**kwargs)
        if (
            plan.execution_allowed
            or not plan.report_required
            or not plan.evidence_required
            or not plan.non_authoritative
            or plan.executed is not False
        ):
            raise ValueError("invalid defensive workflow safety contract")
        return plan


class DefensiveWorkflowRegistry:
    """Phase 10B defensive-workflow registry; unknown workflows are blocked."""

    def __init__(self, definitions: list[DefensiveWorkflowDefinition] | None = None):
        self._definitions: dict[str, DefensiveWorkflowDefinition] = {}
        for definition in definitions or self.default_definitions():
            self.register(definition)

    @staticmethod
    def default_definitions() -> list[DefensiveWorkflowDefinition]:
        return [
            DefensiveWorkflowDefinition(DefensiveWorkflowKind.MALWARE_TRIAGE.value, "Malware Triage", run_malware_triage_workflow),
            DefensiveWorkflowDefinition(DefensiveWorkflowKind.RANSOMWARE_RESPONSE.value, "Ransomware Response", run_ransomware_response_workflow),
            DefensiveWorkflowDefinition(DefensiveWorkflowKind.PHISHING_ATTACHMENT.value, "Phishing Attachment", run_phishing_attachment_workflow),
            DefensiveWorkflowDefinition(DefensiveWorkflowKind.WEBSHELL_INVESTIGATION.value, "Webshell Investigation", run_webshell_investigation_workflow),
            DefensiveWorkflowDefinition(DefensiveWorkflowKind.CREDENTIAL_THEFT.value, "Credential Theft", run_credential_theft_workflow),
            DefensiveWorkflowDefinition(DefensiveWorkflowKind.SUSPICIOUS_PROCESS.value, "Suspicious Process", run_suspicious_process_workflow),
            DefensiveWorkflowDefinition(DefensiveWorkflowKind.DEFENSE_STATUS.value, "Defense Status", run_defense_status_workflow),
        ]

    def register(self, definition: DefensiveWorkflowDefinition) -> None:
        workflow_id = str(definition.workflow_id or "").strip()
        if not workflow_id:
            raise ValueError("defensive workflow_id is required")
        if (
            definition.execution_allowed
            or not definition.report_required
            or not definition.evidence_required
            or not definition.non_authoritative
        ):
            raise ValueError("defensive workflows must be non-executing, non-authoritative, with evidence/report requirements")
        self._definitions[workflow_id] = definition

    def resolve(self, workflow_id: str) -> DefensiveWorkflowDefinition | None:
        return self._definitions.get(str(workflow_id or "").strip())

    def get(self, workflow_id: str) -> DefensiveWorkflowDefinition | None:
        return self.resolve(workflow_id)

    def list_workflows(self) -> list[DefensiveWorkflowDefinition]:
        return list(self._definitions.values())

    def run(self, workflow_id: str, **kwargs) -> DefensiveWorkflowPlan:
        definition = self.get(workflow_id)
        if definition is None:
            raise KeyError(f"unknown defensive workflow blocked: {workflow_id}")
        return definition.run(**kwargs)

    def blocked_unknown(self, workflow_id: str) -> dict:
        return {"workflow_id": workflow_id, "blocked": True, "reason": "unknown_defensive_workflow", "execution_allowed": False}
