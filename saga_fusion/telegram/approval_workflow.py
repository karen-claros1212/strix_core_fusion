import time
import uuid

class ApprovalWorkflow:
    def __init__(self, expiration_minutes=30):
        self.expiration_minutes = expiration_minutes
        self.approvals = {}

    def create_approval(self, mission_id):
        approval_id = str(uuid.uuid4())
        self.approvals[approval_id] = {
            "mission_id": mission_id,
            "expires_at": time.time() + (self.expiration_minutes * 60),
            "status": "PENDING"
        }
        return approval_id

    def is_approved(self, approval_id):
        if approval_id not in self.approvals:
            return False
        approval = self.approvals[approval_id]
        if time.time() > approval['expires_at']:
            approval['status'] = 'EXPIRED'
            return False
        return approval['status'] == 'APPROVED'

    def approve(self, approval_id):
        if approval_id in self.approvals:
            self.approvals[approval_id]['status'] = 'APPROVED'
            return True
        return False
