from __future__ import annotations

from ._helpers import build_plan, classification, iocs, mitre, playbook, sigma, yara


def run_credential_theft_workflow(summary: str = "suspected credential theft", affected_identity: str = "unknown", reported_iocs: list[str] | None = None):
    indicators = ["browser credential store access alert", "unusual sign-in", "token reuse anomaly", "unexpected archive creation telemetry"]
    return build_plan(
        "credential-theft",
        "Credential Theft Defensive Workflow",
        "Identify stealer indicators, evidence paths, and containment recommendations without extracting or displaying secrets.",
        classification=classification("stealer", 0.65, "Credential theft/stealer indicators reported; secrets remain redacted.", ("credential", "stealer")),
        mitre_mappings=mitre(["credential access", "discovery", "command and control"]),
        indicators=iocs(reported_iocs or [affected_identity, "example-stealer-domain.invalid"]),
        evidence={"reported_summary": summary, "stealer_indicators": indicators, "evidence_paths": ["authentication logs", "identity provider alerts", "browser security telemetry", "EDR process/file metadata"], "secret_display": False, "exfiltration": False, "execution_allowed": False},
        yara_rules=yara("strix_stealer_metadata", ["browser credential", "wallet access", "token anomaly"], "Defensive metadata rule for suspected stealer artifacts"),
        sigma_rules=sigma("STRIX Credential Access Signals", {"selection": {"CommandLine|contains": ["Login Data", "Cookies", "keychain"], "Image|endswith": ["\\powershell.exe", "\\cmd.exe"]}}, "Defensive credential-access telemetry correlation", level="high", tags=("attack.credential_access",)),
        playbook=playbook("credential_theft_investigation"),
        checklist=("Identify affected identities", "Collect auth anomalies", "Preserve endpoint telemetry", "Recommend session revocation/credential rotation only", "Never show, copy, or test secrets"),
        recommendations=("Rotate credentials through IAM owner approval", "Revoke active sessions through approved admin channel", "Search for related alerts and mailbox rules", "Notify affected users with approved template"),
        memory_summary={"safe_to_store": True, "fields": ["workflow", "affected_identity_alias", "indicator_count"], "store_secrets": False},
    )
