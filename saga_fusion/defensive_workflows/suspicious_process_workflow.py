from __future__ import annotations

from ._helpers import build_plan, classification, cmd, iocs, mitre, playbook, sigma


def run_suspicious_process_workflow(process_name: str = "unknown", command_line: str = "", parent: str = "", user: str = ""):
    signals = [
        "unexpected parent/child relationship",
        "unusual path or unsigned binary metadata",
        "encoded or long command-line observed in logs",
        "network beacon or abnormal authentication correlation",
    ]
    return build_plan(
        "suspicious-process",
        "Suspicious Process Defensive Workflow",
        "Review suspicious process metadata and propose read-only evidence collection; no termination or host modification is authorized.",
        classification=classification("unknown", 0.45, "Suspicious process review only; no process control action."),
        mitre_mappings=mitre(["defense evasion", "discovery", "command and control"]),
        indicators=iocs([process_name or "unknown_process"]),
        evidence={"process_name": process_name, "parent": parent, "user": user, "signals": signals, "kill_process": False, "execution_allowed": False},
        sigma_rules=sigma("STRIX Suspicious Process Signals", {"selection": {"CommandLine|contains": ["-enc", "frombase64string"], "ParentImage|endswith": ["\\winword.exe", "\\excel.exe"]}}, "Read-only process creation correlation", tags=("attack.defense_evasion", "attack.discovery")),
        playbook=playbook("suspicious_process_review"),
        checklist=("Confirm host and process metadata", "Review parent/child tree", "Correlate auth and network logs", "Preserve evidence before any approved containment", "Do not kill processes in this workflow"),
        recommendations=("Escalate endpoint containment only through approved operations", "Request EDR triage package through official channel", "Document false-positive rationale if benign"),
        suggested_commands=(cmd("ps aux --forest", "List process tree for local lab review only"), cmd("wmic process get ProcessId,ParentProcessId,CommandLine", "Read process metadata in Windows lab only")),
        memory_summary={"safe_to_store": True, "fields": ["workflow", "process_name", "signal_count"], "store_command_line": False},
    )
