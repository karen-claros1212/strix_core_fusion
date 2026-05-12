from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, is_dataclass, replace
from typing import Any

from .types import CompressedContext, SessionSnapshot, SessionState


def canonical_json(payload: Any) -> str:
    def default(value: Any):
        if is_dataclass(value):
            return asdict(value)
        if hasattr(value, "value"):
            return value.value
        return str(value)

    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=default)


def checksum_payload(payload: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def sign_snapshot(snapshot: SessionSnapshot) -> SessionSnapshot:
    return replace(snapshot, checksum=checksum_payload(snapshot.unsigned_dict()))


def verify_snapshot_checksum(snapshot: SessionSnapshot) -> bool:
    return bool(snapshot.checksum) and snapshot.checksum == checksum_payload(snapshot.unsigned_dict())


class SessionSnapshotRegistry:
    """In-memory/file-serializable snapshot registry. It never executes recovered data."""

    def __init__(self):
        self._snapshots: dict[str, SessionSnapshot] = {}

    def add(self, snapshot: SessionSnapshot) -> SessionSnapshot:
        self._snapshots[snapshot.snapshot_id] = snapshot
        return snapshot

    def get(self, snapshot_id: str) -> SessionSnapshot | None:
        return self._snapshots.get(snapshot_id)

    def to_json(self) -> str:
        return canonical_json({sid: snap.to_dict() for sid, snap in self._snapshots.items()})

    @staticmethod
    def snapshot_from_dict(payload: dict[str, Any]) -> SessionSnapshot:
        state_payload = dict(payload["state"])
        state_payload["context"] = tuple(state_payload.get("context") or ())
        state = SessionState(**state_payload)
        compressed = CompressedContext(**payload["compressed_context"])
        return SessionSnapshot(
            snapshot_id=payload["snapshot_id"],
            state=state,
            compressed_context=compressed,
            policy_metadata=dict(payload.get("policy_metadata") or {}),
            created_at=payload["created_at"],
            expires_at=payload["expires_at"],
            checksum=payload.get("checksum", ""),
            version=payload.get("version", "8F-session-recovery-v1"),
        )
