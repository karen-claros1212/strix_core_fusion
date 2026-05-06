class ReplayGuard:
    def __init__(self):
        self.executed_mission_ids = set()

    def mark_executed(self, mission_id: str):
        """Mark a mission ID as executed."""
        self.executed_mission_ids.add(mission_id)

    def is_duplicate(self, mission_id: str) -> bool:
        """Check if a mission ID has already been executed."""
        return mission_id in self.executed_mission_ids
