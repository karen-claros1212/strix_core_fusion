from enum import Enum
from dataclasses import dataclass, field
from typing import Optional
import uuid


class ValidationResult(dict):
    """Dict-like validation result with dual-key compat (allowed + valid)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure legacy 'valid' key mirrors 'allowed'
        if "allowed" in self and "valid" not in self:
            self["valid"] = self["allowed"]
        if "allowed" in self and "errors" not in self:
            self["errors"] = [] if self["allowed"] else [self.get("reason", "Denied")]
        if "valid" in self and "allowed" not in self:
            self["allowed"] = self["valid"]

    def __bool__(self) -> bool:
        return bool(self.get("allowed", False))

class SandboxMode(Enum):
    DRY_RUN = "DRY_RUN"
    LOCAL = "LOCAL"
    DOCKER = "DOCKER"
    WSL = "WSL"
    REAL = "REAL"

class ActionType(Enum):
    EXECUTE = "EXECUTE"
    READ = "READ"
    WRITE = "WRITE"

class RiskLevel(Enum):
    R0 = "R0"
    R1 = "R1"
    R2 = "R2"
    R3 = "R3"
    R4 = "R4"
    R5 = "R5"

@dataclass
class SandboxAction:
    network_target: Optional[str] = None
    action_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    action_type: ActionType = ActionType.EXECUTE
    command: str = ""
    args: list = field(default_factory=list)
    mode: SandboxMode = SandboxMode.DRY_RUN
    workspace_path: str = "/workspace"
    timeout_seconds: int = 300
    risk_level: RiskLevel = RiskLevel.R0
@dataclass
class SandboxResult:
    action_id: str = ""
    success: bool = False
    exit_code: int = 0
    stdout: str = ""
    stderr: str = ""
    duration_seconds: float = 0.0
    message: str = ""
    action: Optional['SandboxAction'] = None
    mode: Optional[str] = None
    executed: bool = False
    returncode: Optional[int] = None
    error: Optional[str] = None


@dataclass
class SandboxConfig:
    workspace_root: str = "/workspace"
    timeout_seconds: int = 300
    allowed_networks: list = field(default_factory=list)
    blocked_networks: list = field(default_factory=list)
    blocked_ports: list = field(default_factory=list)
    ram_limit_mb: float = 512.0
    cpu_limit: float = 1.0
    mode: SandboxMode = SandboxMode.DRY_RUN
