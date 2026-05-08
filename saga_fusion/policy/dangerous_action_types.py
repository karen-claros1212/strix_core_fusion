from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class DangerousActionCategory(str, Enum):
    DESTRUCTIVE_FILESYSTEM = 'destructive_filesystem'
    SECRET_ACCESS = 'secret_access'
    CREDENTIAL_EXFILTRATION = 'credential_exfiltration'
    NETWORK_EXFILTRATION = 'network_exfiltration'
    INFRASTRUCTURE_DESTRUCTION = 'infrastructure_destruction'
    FIREWALL_EXPOSURE = 'firewall_exposure'
    CLOUD_RESOURCE_CREATION = 'cloud_resource_creation'
    CLOUD_RESOURCE_DELETION = 'cloud_resource_deletion'
    BACKUP_DELETION = 'backup_deletion'
    PRIVILEGE_ESCALATION = 'privilege_escalation'
    SANDBOX_BYPASS = 'sandbox_bypass'
    POLICY_BYPASS = 'policy_bypass'
    EVIDENCE_SUPPRESSION = 'evidence_suppression'
    UNKNOWN_HIGH_RISK = 'unknown_high_risk'


class DangerousActionSeverity(str, Enum):
    LOW = 'LOW'
    MEDIUM = 'MEDIUM'
    HIGH = 'HIGH'
    CRITICAL = 'CRITICAL'


@dataclass(frozen=True)
class DangerousActionDecision:
    detected: bool
    categories: list[DangerousActionCategory] = field(default_factory=list)
    severity: DangerousActionSeverity = DangerousActionSeverity.LOW
    risk_level: str = 'R1'
    blocked: bool = False
    approval_required: bool = False
    reason: str = 'no_dangerous_action_detected'
    matched_patterns: list[str] = field(default_factory=list)
    safe_alternative: str = 'Use dry-run/read-only analysis with evidence logging.'
