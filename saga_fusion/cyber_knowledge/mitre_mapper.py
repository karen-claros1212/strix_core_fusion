from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class MitreTechnique:
    tactic: str
    tactic_id: str
    technique_id: str
    technique_name: str
    behavior: str
    defensive_note: str

    def to_dict(self) -> dict:
        return asdict(self)


class MitreMapper:
    """Conservative ATT&CK mapping for defensive triage and reporting."""

    _MAP = {
        "persistence": MitreTechnique("Persistence", "TA0003", "T1547", "Boot or Logon Autostart Execution", "persistence", "Broad defensive mapping; validate against host artifacts."),
        "privilege escalation": MitreTechnique("Privilege Escalation", "TA0004", "T1068", "Exploitation for Privilege Escalation", "privilege escalation", "Use only as a triage hint unless exploit evidence exists."),
        "defense evasion": MitreTechnique("Defense Evasion", "TA0005", "T1027", "Obfuscated Files or Information", "defense evasion", "Conservative behavior mapping for evasion-like observations."),
        "credential access": MitreTechnique("Credential Access", "TA0006", "T1003", "OS Credential Dumping", "credential access", "Investigate credential exposure without reproducing theft behavior."),
        "discovery": MitreTechnique("Discovery", "TA0007", "T1082", "System Information Discovery", "discovery", "Broad discovery mapping for inventory/enumeration observations."),
        "lateral movement": MitreTechnique("Lateral Movement", "TA0008", "T1021", "Remote Services", "lateral movement", "Confirm with authentication and remote-service telemetry."),
        "command and control": MitreTechnique("Command and Control", "TA0011", "T1071", "Application Layer Protocol", "command and control", "Network-beacon mapping for defensive correlation only."),
        "c2": MitreTechnique("Command and Control", "TA0011", "T1071", "Application Layer Protocol", "command and control", "Network-beacon mapping for defensive correlation only."),
        "exfiltration": MitreTechnique("Exfiltration", "TA0010", "T1041", "Exfiltration Over C2 Channel", "exfiltration", "Report suspected data movement; do not implement or test exfiltration."),
        "impact": MitreTechnique("Impact", "TA0040", "T1486", "Data Encrypted for Impact", "impact", "Use as a ransomware/impact investigation starting point."),
    }

    def map_behavior(self, behavior: str) -> MitreTechnique | None:
        key = " ".join(str(behavior or "").lower().replace("_", " ").split())
        return self._MAP.get(key)

    def map_behaviors(self, behaviors) -> list[MitreTechnique]:
        mapped: list[MitreTechnique] = []
        seen: set[tuple[str, str]] = set()
        for behavior in behaviors or []:
            technique = self.map_behavior(str(behavior))
            if technique and (technique.tactic_id, technique.technique_id) not in seen:
                mapped.append(technique)
                seen.add((technique.tactic_id, technique.technique_id))
        return mapped
