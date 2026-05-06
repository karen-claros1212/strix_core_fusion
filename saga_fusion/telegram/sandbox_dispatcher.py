from dataclasses import asdict, is_dataclass
from enum import Enum

from .telegram_types import MissionRequest
from ..runtime.sandbox.sandbox_controller import SandboxController
from ..runtime.sandbox.sandbox_types import SandboxAction, SandboxMode, RiskLevel as SandboxRiskLevel


def _json_safe(value):
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {key: _json_safe(val) for key, val in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


class SandboxDispatcher:
    def __init__(self, sandbox_controller: SandboxController | None):
        self.sandbox_controller = sandbox_controller or SandboxController()

    def _to_sandbox_risk(self, request: MissionRequest) -> SandboxRiskLevel:
        try:
            return SandboxRiskLevel[request.risk_level.name]
        except Exception:
            return SandboxRiskLevel.R0

    def dispatch(self, request: MissionRequest) -> dict:
        """Dispatch a mission request to the sandbox in dry-run mode."""
        action = SandboxAction(
            command=request.action_type or "mission",
            args=request.target.split() if request.target else [],
            mode=SandboxMode.DRY_RUN,
            risk_level=self._to_sandbox_risk(request),
        )
        result = self.sandbox_controller.execute(action)
        payload = asdict(result) if is_dataclass(result) else dict(result)
        payload.update(
            {
                "status": "dry_run" if payload.get("success") else "blocked",
                "executed": False,
                "mode": SandboxMode.DRY_RUN.value,
                "command": action.command,
                "args": action.args,
            }
        )
        if payload.get("action") is not None and is_dataclass(payload["action"]):
            payload["action"] = asdict(payload["action"])
        return _json_safe(payload)
