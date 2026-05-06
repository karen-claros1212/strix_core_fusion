from .telegram_types import MissionStatus

class ApprovalRouter:
    def __init__(self):
        self.pending_approvals = {}

    def route(self, mission_id: str, status: MissionStatus) -> str:
        """Route a mission based on its status."""
        if status == MissionStatus.PENDING:
            return "Approve or Deny"
        elif status == MissionStatus.APPROVED:
            return "Execute"
        elif status == MissionStatus.REJECTED:
            return "Discard"
        return "Unknown"
