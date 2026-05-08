from __future__ import annotations

from .approval_types import ApprovalRiskLevel, ApprovalRequest


class ApprovalPolicy:
    def requires_approval(self, risk_level: str) -> bool:
        return ApprovalRiskLevel(risk_level) == ApprovalRiskLevel.R4

    def is_approvable(self, risk_level: str) -> bool:
        return ApprovalRiskLevel(risk_level) == ApprovalRiskLevel.R4

    def validate_request(self, request: ApprovalRequest, now: float, authorized_users: set[str] | None = None) -> tuple[bool, str]:
        if request.risk_level == ApprovalRiskLevel.R5:
            return False, 'r5_not_approvable'
        if request.risk_level != ApprovalRiskLevel.R4:
            return False, 'only_r4_approvable'
        if not request.mission_id:
            return False, 'missing_mission_id'
        if now > request.expires_at:
            return False, 'approval_expired'
        if authorized_users is not None and request.requested_by not in authorized_users:
            return False, 'requester_not_authorized'
        return True, 'approval_request_valid'
