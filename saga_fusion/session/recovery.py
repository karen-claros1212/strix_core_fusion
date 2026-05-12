from __future__ import annotations

from dataclasses import replace
import uuid
from typing import Any

from saga_fusion.memory import MemoryRedactor

from .compressor import ContextCompressor
from .policy import RecoveryPolicyError, SessionRecoveryPolicy
from .registry import sign_snapshot, verify_snapshot_checksum
from .types import RecoveryRecord, RecoveryStatus, SessionSnapshot, SessionState, utc_after, utc_now


class SnapshotIntegrityError(ValueError):
    pass


class SnapshotExpiredError(ValueError):
    pass


class SessionRecoveryManager:
    """Metadata-only session recovery. No tool, gateway, or command execution exists here."""

    def __init__(self, policy: SessionRecoveryPolicy | None = None, compressor: ContextCompressor | None = None, redactor: MemoryRedactor | None = None):
        self.policy = policy or SessionRecoveryPolicy()
        self.redactor = redactor or MemoryRedactor()
        self.compressor = compressor or ContextCompressor(policy=self.policy, redactor=self.redactor)

    def create_snapshot(self, state: SessionState, *, budget_chars: int | None = None, ttl_seconds: int | None = None) -> SessionSnapshot:
        safe_intent = self.redactor.redact_text(state.user_intent)
        safe_metadata = self.redactor.redact(state.metadata)
        safe_context = tuple(state.context or ())
        if safe_intent.secret_blocked:
            safe_user_intent = "[REDACTED_SECRET_BEARING_INTENT_EXCLUDED]"
        else:
            safe_user_intent = safe_intent.text
        compressed = self.compressor.compress(safe_context, budget_chars=budget_chars)
        safe_state = replace(
            state,
            user_intent=safe_user_intent,
            context=(),  # raw context is never carried in snapshots; only inert compressed context is retained.
            metadata=safe_metadata if isinstance(safe_metadata, dict) else {},
        )
        snapshot = SessionSnapshot(
            snapshot_id=f"snapshot-{uuid.uuid4().hex[:12]}",
            state=safe_state,
            compressed_context=compressed,
            policy_metadata=self.policy.metadata(),
            created_at=utc_now(),
            expires_at=utc_after(self.policy.ttl_seconds if ttl_seconds is None else ttl_seconds),
        )
        return sign_snapshot(snapshot)

    def recover(self, snapshot: SessionSnapshot | dict[str, Any], *, live_risk_level: str | None = None) -> RecoveryRecord:
        if isinstance(snapshot, dict):
            from .registry import SessionSnapshotRegistry

            snapshot = SessionSnapshotRegistry.snapshot_from_dict(snapshot)
        self.policy.assert_recoverable_metadata(snapshot.policy_metadata)
        if not verify_snapshot_checksum(snapshot):
            raise SnapshotIntegrityError("snapshot_checksum_invalid")
        if self.policy.is_expired(snapshot.expires_at):
            raise SnapshotExpiredError("snapshot_expired")
        effective = self.policy.enforce_recovered_risk(live_risk_level, snapshot.state.risk_level)
        recovered_state = snapshot.state.with_risk(effective)
        return RecoveryRecord(
            snapshot_id=snapshot.snapshot_id,
            recovered_state=recovered_state,
            compressed_context=snapshot.compressed_context,
            status=RecoveryStatus.RECOVERED,
            reason="snapshot_recovered_as_non_authoritative_metadata_only",
            policy_metadata=self.policy.metadata(),
        )

    def reject_record(self, snapshot_id: str, reason: str) -> RecoveryRecord:
        return RecoveryRecord(
            snapshot_id=snapshot_id,
            recovered_state=None,
            compressed_context=None,
            status=RecoveryStatus.REJECTED,
            reason=reason,
            policy_metadata=self.policy.metadata(),
        )
