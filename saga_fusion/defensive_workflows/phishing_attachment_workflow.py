from __future__ import annotations

from ._helpers import build_plan, classification, iocs, mitre, playbook, sigma, yara


def run_phishing_attachment_workflow(subject: str = "reported phishing", attachment_name: str = "unknown", sender: str = "unknown"):
    return build_plan(
        "phishing-attachment",
        "Phishing Attachment Defensive Workflow",
        "Perform conceptual static-analysis planning, indicators, defensive rules, and containment recommendations without opening or executing attachments.",
        classification=classification("trojan", 0.5, "Phishing attachment reported; static metadata review only."),
        mitre_mappings=mitre(["defense evasion", "credential access", "command and control"]),
        indicators=iocs([sender, attachment_name, subject]),
        evidence={"static_analysis_concepts": ["headers", "sender reputation context", "attachment name/hash", "macro/embedded-object metadata if already available"], "attachment_execution": False, "detonation": False, "execution_allowed": False},
        yara_rules=yara("strix_phishing_attachment_metadata", ["invoice", "urgent payment", "macro document"], "Defensive metadata rule for phishing attachment review"),
        sigma_rules=sigma("STRIX Phishing Attachment Process Signals", {"selection": {"ParentImage|endswith": ["\\winword.exe", "\\excel.exe", "\\outlook.exe"], "Image|endswith": ["\\powershell.exe", "\\cmd.exe"]}}, "Defensive post-delivery process correlation", tags=("attack.defense_evasion",)),
        playbook=playbook("phishing_attachment_review"),
        checklist=("Record headers and recipients", "Hash attachment only through approved tooling", "Review static metadata or trusted sandbox report references", "Search mailboxes for same indicators", "Do not open, enable content, or execute attachments"),
        recommendations=("Quarantine matching messages through approved mail workflow", "Notify recipients", "Block sender/domain if validated", "Create detection ticket for similar lure metadata"),
        memory_summary={"safe_to_store": True, "fields": ["workflow", "subject_summary", "attachment_name", "sender_alias"], "store_attachment_body": False},
    )
