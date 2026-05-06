from enum import Enum
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

class DecisionType(Enum):
    ALLOWED = "allowed"
    DENIED = "denied"
    SANITIZED = "sanitized"

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SecurityDecision:
    allowed: bool
    risk_level: RiskLevel
    reason: str
    sanitized_action: Optional[Dict[str, Any]] = None
    action_fingerprint: str = ""

@dataclass
class ToolResult:
    success: bool
    content: str
    status: str  # "SUCCESS", "DENIED", "ERROR"
    decision: Optional[SecurityDecision] = None