from __future__ import annotations

import time

from .approval_store import ApprovalStore
from .approval_types import ApprovalDecision, ApprovalRiskLevel, ApprovalStatus


class ApprovalVerifier:
    def __init__(self, store: ApprovalStore):
        self.store = store

    def _evidence(self, *, approval_id: str, reason: str, status: ApprovalStatus, request=None, now: float | None = None) -> dict:
        evidence = {
            'approval_id': str(approval_id),
            'status': status.value,
            'reason': reason,
            'execution_allowed': False,
            'approval_terminal': status != ApprovalStatus.PENDING,
        }
        if request is not None:
            evidence.update({
                'mission_id': request.mission_id,
                'risk_level': request.risk_level.value,
                'expires_at': request.expires_at,
                'seconds_until_expiry': request.seconds_until_expiry(now if now is not None else time.time()),
                'action_hash': request.action_hash,
                'used': request.used,
            })
        return evidence

    def verify(self, approval_id: str, *, action_hash: str, user_id: str, authorized_users: set[str], now: float | None = None) -> ApprovalDecision:
        current = float(now if now is not None else time.time())
        request = self.store.get(approval_id)
        if not request:
            return ApprovalDecision(False, ApprovalStatus.BLOCKED, 'approval_not_found', approval_id, self._evidence(approval_id=approval_id, reason='approval_not_found', status=ApprovalStatus.BLOCKED, now=current))
        if request.risk_level == ApprovalRiskLevel.R5:
            request.status = ApprovalStatus.BLOCKED
            return ApprovalDecision(False, ApprovalStatus.BLOCKED, 'r5_not_approvable', approval_id, self._evidence(approval_id=approval_id, reason='r5_not_approvable', status=ApprovalStatus.BLOCKED, request=request, now=current))
        if request.used:
            request.status = ApprovalStatus.USED
            return ApprovalDecision(False, ApprovalStatus.USED, 'approval_replay_blocked', approval_id, self._evidence(approval_id=approval_id, reason='approval_replay_blocked', status=ApprovalStatus.USED, request=request, now=current))
        if request.status != ApprovalStatus.PENDING:
            reason_by_status = {
                ApprovalStatus.DENIED: 'approval_denied_irreversible',
                ApprovalStatus.EXPIRED: 'approval_expired_irreversible',
                ApprovalStatus.INVALID_HASH: 'approval_hash_mismatch_irreversible',
                ApprovalStatus.APPROVED: 'approval_already_approved',
                ApprovalStatus.USED: 'approval_replay_blocked',
                ApprovalStatus.BLOCKED: 'approval_blocked_irreversible',
            }
            reason = reason_by_status.get(request.status, 'approval_not_pending')
            return ApprovalDecision(False, request.status, reason, approval_id, self._evidence(approval_id=approval_id, reason=reason, status=request.status, request=request, now=current))
        if request.is_expired(current):
            request.status = ApprovalStatus.EXPIRED
            return ApprovalDecision(False, ApprovalStatus.EXPIRED, 'approval_expired', approval_id, self._evidence(approval_id=approval_id, reason='approval_expired', status=ApprovalStatus.EXPIRED, request=request, now=current))
        if action_hash != request.action_hash:
            request.status = ApprovalStatus.INVALID_HASH
            return ApprovalDecision(False, ApprovalStatus.INVALID_HASH, 'action_hash_mismatch', approval_id, self._evidence(approval_id=approval_id, reason='action_hash_mismatch', status=ApprovalStatus.INVALID_HASH, request=request, now=current))
        if str(user_id) not in {str(user) for user in authorized_users}:
            return ApprovalDecision(False, ApprovalStatus.BLOCKED, 'approver_not_authorized', approval_id, self._evidence(approval_id=approval_id, reason='approver_not_authorized', status=ApprovalStatus.BLOCKED, request=request, now=current))
        request.status = ApprovalStatus.APPROVED
        return ApprovalDecision(True, ApprovalStatus.APPROVED, 'approval_verified_non_executing', approval_id, self._evidence(approval_id=approval_id, reason='approval_verified_non_executing', status=ApprovalStatus.APPROVED, request=request, now=current))
