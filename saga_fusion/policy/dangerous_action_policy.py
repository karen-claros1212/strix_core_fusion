from __future__ import annotations

from .dangerous_action_detector import DangerousActionDetector, DangerousActionMatch
from .dangerous_action_types import DangerousActionCategory, DangerousActionDecision, DangerousActionSeverity

BLOCK_CATEGORIES = {
    DangerousActionCategory.DESTRUCTIVE_FILESYSTEM,
    DangerousActionCategory.CREDENTIAL_EXFILTRATION,
    DangerousActionCategory.NETWORK_EXFILTRATION,
    DangerousActionCategory.INFRASTRUCTURE_DESTRUCTION,
    DangerousActionCategory.CLOUD_RESOURCE_DELETION,
    DangerousActionCategory.BACKUP_DELETION,
    DangerousActionCategory.PRIVILEGE_ESCALATION,
    DangerousActionCategory.SANDBOX_BYPASS,
    DangerousActionCategory.POLICY_BYPASS,
    DangerousActionCategory.EVIDENCE_SUPPRESSION,
}
R4_CATEGORIES = {DangerousActionCategory.CLOUD_RESOURCE_CREATION, DangerousActionCategory.UNKNOWN_HIGH_RISK}

SEVERITY_ORDER = {
    DangerousActionSeverity.LOW: 1,
    DangerousActionSeverity.MEDIUM: 2,
    DangerousActionSeverity.HIGH: 3,
    DangerousActionSeverity.CRITICAL: 4,
}


class DangerousActionPolicy:
    def __init__(self, detector: DangerousActionDetector | None = None):
        self.detector = detector or DangerousActionDetector()

    def evaluate(self, text: str, context=None) -> DangerousActionDecision:
        return self.decide(self.detector.detect(text), text=text, context=context)

    def decide(self, matches: list[DangerousActionMatch], text: str = '', context=None) -> DangerousActionDecision:
        if not matches:
            lowered = (text or '').lower()
            if any(word in lowered for word in ('exploit', 'unknown tool', 'herramienta desconocida')):
                return DangerousActionDecision(True, [DangerousActionCategory.UNKNOWN_HIGH_RISK], DangerousActionSeverity.HIGH, 'R4', False, True, 'unknown_high_risk_requires_approval', ['unknown_high_risk'])
            return DangerousActionDecision(False)
        categories = []
        category_set = set()
        patterns = []
        severity = DangerousActionSeverity.LOW
        for match in matches:
            if match.category not in category_set:
                categories.append(match.category)
                category_set.add(match.category)
            patterns.append(match.pattern_name)
            if SEVERITY_ORDER[match.severity] > SEVERITY_ORDER[severity]:
                severity = match.severity
        pattern_set = set(patterns)
        if DangerousActionCategory.FIREWALL_EXPOSURE in category_set:
            if pattern_set & {'disable_firewall','allow_all_inbound'}:
                return DangerousActionDecision(True, categories, DangerousActionSeverity.CRITICAL, 'R5', True, False, 'firewall_exposure_r5_blocked', patterns)
            return DangerousActionDecision(True, categories, severity, 'R4', False, True, 'firewall_exposure_requires_approval', patterns)
        if DangerousActionCategory.SECRET_ACCESS in category_set and DangerousActionCategory.CREDENTIAL_EXFILTRATION not in category_set:
            return DangerousActionDecision(True, categories, severity, 'R5', True, False, 'secret_access_blocked_without_explicit_audit_scope', patterns)
        if category_set & BLOCK_CATEGORIES:
            return DangerousActionDecision(True, categories, DangerousActionSeverity.CRITICAL, 'R5', True, False, 'dangerous_action_r5_blocked', patterns)
        if category_set & R4_CATEGORIES:
            return DangerousActionDecision(True, categories, severity, 'R4', False, True, 'dangerous_action_r4_requires_approval', patterns)
        return DangerousActionDecision(True, categories, severity, 'R4', False, True, 'dangerous_action_escalated_to_r4', patterns)
