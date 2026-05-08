from __future__ import annotations

import time

from .approval_store import ApprovalStore
from .approval_types import ApprovalDecision, ApprovalRiskLevel, ApprovalStatus


class ApprovalVerifier:
    def __init__(self, store: ApprovalStore):
        self.store = store

    def verify(self, approval_id: str, *, action_hash: str, user_id: str, authorized_users: set[str], now: float | None = None) -> ApprovalDecision:
        current = float(now if now is not None else time.time())
        request = self.store.get(approval_id)
        if not request:
            return ApprovalDecision(False, ApprovalStatus.BLOCKED, 'approval_not_found', approval_id)
        if request.risk_level == ApprovalRiskLevel.R5:
            request.status = ApprovalStatus.BLOCKED
            return ApprovalDecision(False, ApprovalStatus.BLOCKED, 'r5_not_approvable', approval_id)
        if request.status != ApprovalStatus.PENDING:
            status = ApprovalStatus.USED if request.used else request.status
            return ApprovalDecision(False, status, 'approval_not_pending', approval_id)
        if current > request.expires_at:
            request.status = ApprovalStatus.EXPIRED
            return ApprovalDecision(False, ApprovalStatus.EXPIRED, 'approval_expired', approval_id)
        if request.used:
            request.status = ApprovalStatus.USED
            return ApprovalDecision(False, ApprovalStatus.USED, 'approval_replay_blocked', approval_id)
        if action_hash != request.action_hash:
            request.status = ApprovalStatus.INVALID_HASH
            return ApprovalDecision(False, ApprovalStatus.INVALID_HASH, 'action_hash_mismatch', approval_id)
        if str(user_id) not in authorized_users:
            return ApprovalDecision(False, ApprovalStatus.BLOCKED, 'approver_not_authorized', approval_id)
        request.status = ApprovalStatus.APPROVED
        return ApprovalDecision(True, ApprovalStatus.APPROVED, 'approval_verified', approval_id, {'mission_id': request.mission_id, 'action_hash': request.action_hash})
