from __future__ import annotations

import hashlib
import json
import time
import uuid
from enum import Enum
from dataclasses import asdict, is_dataclass
from typing import Any

from .approval_types import ApprovalRequest, ApprovalRiskLevel


def _json_safe(value: Any):
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return {k: _json_safe(v) for k, v in asdict(value).items()}
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    return value


class ApprovalRequestBuilder:
    def __init__(self, expiration_minutes: int = 30):
        self.expiration_minutes = expiration_minutes

    def compute_action_hash(self, action_payload) -> str:
        canonical = json.dumps(_json_safe(action_payload), sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical.encode('utf-8')).hexdigest()

    def build(self, *, mission_id: str, action_payload: dict, canonical_action: str, risk_level: str, requested_by: str, reason: str = '', summary: str = '', rollback_plan: str = '', before_state: str = '', evidence_ref: str = '', now: float | None = None) -> ApprovalRequest:
        risk = ApprovalRiskLevel(risk_level)
        if risk == ApprovalRiskLevel.R5:
            raise ValueError('R5 actions are not approvable')
        if risk != ApprovalRiskLevel.R4:
            raise ValueError('Only R4 actions require ApprovalRequest')
        created = float(now if now is not None else time.time())
        return ApprovalRequest(
            approval_id=str(uuid.uuid4()),
            mission_id=str(mission_id),
            action_hash=self.compute_action_hash(action_payload),
            canonical_action=str(canonical_action),
            risk_level=risk,
            requested_by=str(requested_by),
            created_at=created,
            expires_at=created + self.expiration_minutes * 60,
            reason=reason or 'R4 action requires explicit approval',
            summary=summary or f'Approve R4 action {canonical_action}',
            rollback_plan=rollback_plan or 'Use provider-specific rollback plan before execution.',
            before_state=before_state or 'unknown_before_state',
            evidence_ref=evidence_ref or f'mission:{mission_id}',
        )
