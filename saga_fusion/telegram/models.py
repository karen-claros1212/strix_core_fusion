from enum import Enum
from dataclasses import dataclass, field
from typing import Optional
import uuid
from datetime import datetime

class RiskLevel(Enum):
    R0 = "R0"
    R1 = "R1"
    R2 = "R2"
    R3 = "R3"
    R4 = "R4"
    R5 = "R5"

class MissionStatus(Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    EXECUTED = "EXECUTED"
    FAILED = "FAILED"

@dataclass
class MissionRequest:
    mission_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    requester_id: str = ""
    chat_id: str = ""
    raw_text: str = ""
    action_type: str = ""
    target: str = ""
    arguments: str = ""
    risk_level: RiskLevel = RiskLevel.R0
    status: MissionStatus = MissionStatus.PENDING
    approval_id: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
