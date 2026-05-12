from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class ApprovalRegressionCase:
    case_id: str
    risk_level: str
    attempt: str
    expected_status: str
    expected_reason: str
    execution_allowed: bool = False
    real_execution: bool = False

    def to_metadata(self) -> dict:
        return asdict(self)


class ApprovalRegressionMatrix:
    """Metadata-only approval regression coverage; never executes actions."""

    DEFAULT_CASES = (
        ApprovalRegressionCase('r4_valid_non_executing', 'R4', 'authorized_exact_hash_before_expiry', 'APPROVED', 'approval_verified_non_executing'),
        ApprovalRegressionCase('r5_non_approvable', 'R5', 'approval_attempt', 'BLOCKED', 'r5_not_approvable'),
        ApprovalRegressionCase('expired_at_ttl', 'R4', 'at_or_after_expiry', 'EXPIRED', 'approval_expired'),
        ApprovalRegressionCase('replay_used', 'R4', 'used_approval_second_attempt', 'USED', 'approval_replay_blocked'),
        ApprovalRegressionCase('hash_mismatch', 'R4', 'wrong_action_hash', 'INVALID_HASH', 'action_hash_mismatch'),
        ApprovalRegressionCase('unauthorized_actor', 'R4', 'actor_not_allowlisted', 'BLOCKED', 'approver_not_authorized'),
        ApprovalRegressionCase('denied_irreversible', 'R4', 'approve_after_deny', 'DENIED', 'approval_denied_irreversible'),
        ApprovalRegressionCase('nonexistent_approval', 'R4', 'unknown_approval_id', 'BLOCKED', 'approval_not_found'),
    )

    def __init__(self, cases: tuple[ApprovalRegressionCase, ...] | None = None):
        self.cases = tuple(cases or self.DEFAULT_CASES)

    def to_manifest(self) -> dict:
        return {
            'component': 'saga_fusion.approval',
            'phase': '8I',
            'execution_allowed': False,
            'case_count': len(self.cases),
            'cases': [case.to_metadata() for case in self.cases],
        }
