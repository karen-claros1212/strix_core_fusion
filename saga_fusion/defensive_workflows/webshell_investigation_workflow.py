from __future__ import annotations

from ._helpers import build_plan, classification, iocs, mitre, playbook, sigma, yara


def run_webshell_investigation_workflow(web_root: str = "unknown", suspicious_path: str = "unknown"):
    indicators = ["recently modified script under web root", "unexpected POST requests", "short high-entropy parameter names", "web server user spawning shell utility telemetry"]
    return build_plan(
        "webshell-investigation",
        "Webshell Investigation Defensive Workflow",
        "Review suspected webshell indicators, paths, and logs with defensive rules; no webshell generation or endpoint invocation.",
        classification=classification("backdoor", 0.6, "Suspected webshell/backdoor investigation only; no interactive access."),
        mitre_mappings=mitre(["persistence", "command and control", "defense evasion"]),
        indicators=iocs([web_root, suspicious_path, "access.log"]),
        evidence={"webshell_indicators": indicators, "typical_paths": ["web root uploads", "temporary web directories", "plugin/theme directories", "unexpected script extensions"], "logs_to_review": ["access logs", "error logs", "file integrity events", "process creation logs"], "webshell_generation": False, "endpoint_invocation": False, "execution_allowed": False},
        yara_rules=yara("strix_webshell_metadata", ["eval request", "cmd parameter", "uploaded script"], "Defensive metadata rule for suspected webshell artifacts"),
        sigma_rules=sigma("STRIX Web Server Child Process Signals", {"selection": {"ParentImage|contains": ["apache", "nginx", "w3wp"], "Image|endswith": ["\\cmd.exe", "\\powershell.exe", "/bin/sh"]}}, "Defensive web server process correlation", level="high", tags=("attack.persistence", "attack.command_and_control")),
        playbook=playbook("webshell_investigation"),
        checklist=("Inventory recently changed web files", "Correlate requests with file writes", "Review web server child process telemetry", "Prepare removal recommendation for approved maintenance", "Do not generate or call a webshell"),
        recommendations=("Preserve suspicious files by approved forensic process", "Restrict upload paths after approval", "Rotate app credentials if compromise confirmed", "Add detection coverage for web server child processes"),
        memory_summary={"safe_to_store": True, "fields": ["workflow", "web_root_alias", "suspicious_path_alias"], "store_file_contents": False},
    )
