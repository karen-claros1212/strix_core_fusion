from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Any


@dataclass(frozen=True)
class IncidentPlaybook:
    playbook_id: str
    title: str
    objective: str
    steps: tuple[str, ...]
    evidence_to_collect: tuple[str, ...]
    containment_notes: tuple[str, ...]
    execution_allowed: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class IncidentPlaybookRegistry:
    def __init__(self):
        self._playbooks = {p.playbook_id: p for p in self._defaults()}

    def get(self, playbook_id: str) -> IncidentPlaybook | None:
        return self._playbooks.get(str(playbook_id or "").strip().lower())

    def list_playbooks(self) -> list[IncidentPlaybook]:
        return list(self._playbooks.values())

    def select(self, text: str) -> IncidentPlaybook | None:
        normalized = str(text or "").lower()
        aliases = {
            "malware_triage": ("malware", "triage"),
            "suspicious_process_review": ("process", "suspicious process"),
            "credential_theft_investigation": ("credential", "password", "token theft", "stealer"),
            "ransomware_containment_plan": ("ransomware", "encrypt", "ransom"),
            "webshell_investigation": ("webshell", "web shell", "uploaded shell"),
            "phishing_attachment_review": ("phishing", "attachment", "email attachment"),
        }
        for playbook_id, terms in aliases.items():
            if any(term in normalized for term in terms):
                return self.get(playbook_id)
        return None

    @staticmethod
    def _defaults() -> tuple[IncidentPlaybook, ...]:
        safety = {"defensive_only": True, "no_execution": True, "no_real_containment": True}
        return (
            IncidentPlaybook("malware_triage", "Malware Triage", "Classify reported indicators and prioritize evidence review.", ("Record source and scope.", "Classify reported behaviors with taxonomy.", "Map behaviors to MITRE ATT&CK.", "Draft detections from static metadata only."), ("hashes", "file paths", "process names", "alert timestamps"), ("Plan isolation only through approved operations; do not execute samples."), False, safety),
            IncidentPlaybook("suspicious_process_review", "Suspicious Process Review", "Review process metadata and parent/child relationships defensively.", ("Collect process name, path, user, parent, and command-line metadata.", "Compare against expected administration tools.", "Prepare Sigma-style log correlation."), ("process metadata", "host logs", "user context"), ("Escalate to approved endpoint workflow before termination."), False, safety),
            IncidentPlaybook("credential_theft_investigation", "Credential Theft Investigation", "Investigate suspected credential access without reproducing theft.", ("Identify affected identities and systems.", "Review authentication anomalies.", "Recommend rotation and session revocation via approved channels."), ("auth logs", "identity alerts", "reported IoCs"), ("Use approved IAM procedures only; never extract credentials."), False, safety),
            IncidentPlaybook("ransomware_containment_plan", "Ransomware Containment Plan", "Plan containment and recovery for suspected ransomware impact.", ("Confirm scope from alerts and file-change metadata.", "Prioritize backup and restore readiness checks.", "Draft communications and containment approvals."), ("ransom notes", "file-change telemetry", "backup status", "host list"), ("Containment actions require human approval and operational runbooks."), False, safety),
            IncidentPlaybook("webshell_investigation", "Webshell Investigation", "Review suspected webshell artifacts defensively.", ("Inventory recently modified web paths.", "Correlate web server logs with file-write times.", "Create metadata-only detection hints."), ("web paths", "server logs", "file hashes"), ("Do not invoke suspected webshell endpoints."), False, safety),
            IncidentPlaybook("phishing_attachment_review", "Phishing Attachment Review", "Review reported phishing attachment metadata safely.", ("Record sender, subject, attachment name, hash, and sandbox report references.", "Map lure and attachment behavior to defensive categories.", "Recommend user notification and mailbox search."), ("message headers", "attachment hashes", "recipient list"), ("Do not open or execute attachments."), False, safety),
        )
