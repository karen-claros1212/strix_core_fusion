import json
from datetime import datetime

class TelegramAudit:
    def __init__(self):
        self.logs = []

    def log(self, chat_id, user_id, action, details):
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "chat_id": chat_id,
            "user_id": user_id,
            "action": action,
            "details": details
        }
        self.logs.append(entry)
        return entry
