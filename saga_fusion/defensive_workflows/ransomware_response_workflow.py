from __future__ import annotations

from ._helpers import build_plan, classification, iocs, mitre, playbook, sigma, yara


def run_ransomware_response_workflow(incident_summary: str = "suspected ransomware", affected_scope: str = "unknown"):
    return build_plan(
        "ransomware-response",
        "Ransomware Response Defensive Workflow",
        "Plan triage, evidence preservation, isolation recommendations, and backup review without deleting, encrypting, or decrypting files.",
        classification=classification("ransomware", 0.7, "Ransomware/impact triage plan only; operational actions require separate approval.", ("ransomware", "impact")),
        mitre_mappings=mitre(["impact", "lateral movement", "credential access", "command and control"]),
        indicators=iocs([affected_scope, "ransom_note_name_placeholder", "file_extension_change_placeholder"]),
        evidence={"triage": ["scope affected hosts", "identify first-seen timestamp", "record ransom note metadata"], "isolation_recommended": True, "isolation_executed": False, "snapshot_backup_review_plan": True, "file_deletion": False, "encryption_decryption": False, "execution_allowed": False},
        yara_rules=yara("strix_ransomware_metadata", ["ransom note", "encrypted files", "restore instructions"], "Defensive metadata rule for ransomware triage"),
        sigma_rules=sigma("STRIX Ransomware Impact Signals", {"selection": {"CommandLine|contains": ["vssadmin", "shadowcopy", "bcdedit"], "Image|endswith": ["\\powershell.exe", "\\cmd.exe"]}}, "Defensive impact telemetry correlation", level="high", tags=("attack.impact",)),
        playbook=playbook("ransomware_containment_plan"),
        checklist=("Triage scope and business impact", "Preserve volatile/log evidence", "Recommend isolation through approved runbook", "Review snapshots/backups as plan", "Do not delete files or run encryption/decryption"),
        recommendations=("Open incident bridge", "Prioritize identity and backup integrity checks", "Prepare isolation approval request", "Coordinate restore validation with owners"),
        memory_summary={"safe_to_store": True, "fields": ["workflow", "scope_alias", "triage_status"], "store_ransom_note_body": False},
    )
