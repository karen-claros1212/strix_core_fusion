import hashlib
import json
import time
import uuid
from dataclasses import asdict, is_dataclass
from enum import Enum
from typing import Any


def _json_safe(value: Any):
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return {key: _json_safe(val) for key, val in asdict(value).items()}
    if isinstance(value, dict):
        return {str(key): _json_safe(val) for key, val in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value


class ApprovalWorkflow:
    def __init__(self, expiration_minutes=30):
        self.expiration_minutes = expiration_minutes
        self.approvals = {}
        self.used_action_hashes = set()

    def compute_action_hash(self, action_payload) -> str:
        canonical = json.dumps(_json_safe(action_payload), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def create_approval(self, mission_id, action_payload=None):
        approval_id = str(uuid.uuid4())
        payload = action_payload if action_payload is not None else {"mission_id": mission_id}
        action_hash = self.compute_action_hash(payload)
        self.approvals[approval_id] = {
            "mission_id": str(mission_id),
            "action_hash": action_hash,
            "expires_at": time.time() + (self.expiration_minutes * 60),
            "status": "PENDING",
        }
        return approval_id

    def get_action_hash(self, approval_id):
        approval = self.approvals.get(approval_id)
        return approval.get("action_hash") if approval else None

    def is_approved(self, approval_id):
        approval = self.approvals.get(approval_id)
        if not approval:
            return False
        if time.time() > approval["expires_at"]:
            approval["status"] = "EXPIRED"
            return False
        return approval["status"] == "APPROVED"

    def approve(self, approval_id, action_payload=None, action_hash=None):
        approval = self.approvals.get(approval_id)
        if not approval:
            return False
        if time.time() > approval["expires_at"]:
            approval["status"] = "EXPIRED"
            return False
        expected_hash = approval["action_hash"]
        candidate_hash = action_hash or (self.compute_action_hash(action_payload) if action_payload is not None else expected_hash)
        if candidate_hash != expected_hash:
            approval["status"] = "HASH_MISMATCH"
            return False
        if expected_hash in self.used_action_hashes:
            approval["status"] = "REPLAY_BLOCKED"
            return False
        self.used_action_hashes.add(expected_hash)
        approval["status"] = "APPROVED"
        return True

    def deny(self, approval_id):
        if approval_id in self.approvals:
            self.approvals[approval_id]["status"] = "REJECTED"
            return True
        return False
