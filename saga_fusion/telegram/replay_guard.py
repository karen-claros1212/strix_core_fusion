class ReplayGuard:
    def __init__(self):
        self.executed_mission_ids = set()
        self.consumed_action_hashes = set()

    def mark_executed(self, mission_id: str):
        self.executed_mission_ids.add(str(mission_id))

    def is_duplicate(self, mission_id: str) -> bool:
        return str(mission_id) in self.executed_mission_ids

    def consume_action_hash(self, action_hash: str) -> bool:
        if not action_hash:
            return False
        if action_hash in self.consumed_action_hashes:
            return False
        self.consumed_action_hashes.add(action_hash)
        return True
