from __future__ import annotations

from .approval_types import ApprovalRequest, ApprovalStatus


class ApprovalStore:
    def __init__(self):
        self._items: dict[str, ApprovalRequest] = {}

    def create(self, request: ApprovalRequest) -> ApprovalRequest:
        self._items[request.approval_id] = request
        return request

    def get(self, approval_id: str) -> ApprovalRequest | None:
        return self._items.get(str(approval_id))

    def mark_approved(self, approval_id: str) -> bool:
        item = self.get(approval_id)
        if not item:
            return False
        item.status = ApprovalStatus.APPROVED
        return True

    def mark_denied(self, approval_id: str) -> bool:
        item = self.get(approval_id)
        if not item:
            return False
        item.status = ApprovalStatus.DENIED
        return True

    def mark_used(self, approval_id: str) -> bool:
        item = self.get(approval_id)
        if not item:
            return False
        item.used = True
        item.status = ApprovalStatus.USED
        return True

    def expire_old(self, now: float) -> int:
        count = 0
        for item in self._items.values():
            if item.status == ApprovalStatus.PENDING and now > item.expires_at:
                item.status = ApprovalStatus.EXPIRED
                count += 1
        return count
