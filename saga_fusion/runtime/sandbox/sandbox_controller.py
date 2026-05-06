from .sandbox_types import SandboxConfig, SandboxAction, SandboxResult, RiskLevel, SandboxMode
from .sandbox_policy import SandboxPolicy
from .filesystem_jailer import FilesystemJailer
from .network_jailer import NetworkJailer
from .resource_limiter import ResourceLimiter
import subprocess
import time

class SandboxController:
    def __init__(self, config: SandboxConfig = None):
        self.config = config if config is not None else SandboxConfig()
        self.policy = SandboxPolicy(config)
        self.fs_jailer = FilesystemJailer(config)
        self.net_jailer = NetworkJailer(config)
        self.res_limiter = ResourceLimiter(config)

    def _validation_allowed(self, result) -> bool:
        if isinstance(result, dict):
            return bool(result.get("allowed", False))
        return bool(result)

    def _effective_mode(self, action: SandboxAction) -> SandboxMode:
        mode = self.config.mode if self.config is not None else SandboxMode.DRY_RUN
        if isinstance(mode, str):
            normalized = mode.strip().upper()
            for candidate in SandboxMode:
                if candidate.value == normalized or candidate.name == normalized:
                    return candidate
            if normalized == "DRY_RUN":
                return SandboxMode.DRY_RUN
            if normalized == "LOCAL":
                return SandboxMode.LOCAL
        if isinstance(mode, SandboxMode):
            return mode
        return action.mode if isinstance(action.mode, SandboxMode) else SandboxMode.DRY_RUN

    def validate_action(self, action: SandboxAction) -> bool:
        """Run all validation checks before execution."""
        if not self._validation_allowed(self.policy.validate_command(action)):
            return False
        
        if action.workspace_path:
            if not self.fs_jailer.is_safe_path(action.workspace_path):
                return False
        
        if action.network_target:
            if not self._validation_allowed(self.net_jailer.validate_network(action.network_target)):
                return False
                
        return True

    def execute(self, action: SandboxAction) -> SandboxResult:
        """Execute the sandboxed action."""
        if not self.validate_action(action):
            return SandboxResult(
                success=False,
                message="Action blocked by Sandbox Policy",
                action=action
            )

        if self._effective_mode(action) == SandboxMode.DRY_RUN:
            return SandboxResult(
                success=True,
                message="Dry run successful",
                action=action
            )

        try:
            # Execute command with timeout
            result = subprocess.run(
                [action.command] + action.args,
                capture_output=True,
                text=True,
                timeout=self.res_limiter.get_timeout()
            )

            return SandboxResult(
                success=result.returncode == 0,
                message="Execution completed",
                action=action,
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr
            )
        except subprocess.TimeoutExpired:
            return SandboxResult(
                success=False,
                message="Execution timed out",
                action=action
            )
        except Exception as e:
            return SandboxResult(
                success=False,
                message=str(e),
                action=action
            )
            return SandboxResult(
                success=True,
                message="Dry run successful",
                action=action,
                executed=False
            )
            return SandboxResult(
                success=result.returncode == 0,
                message="Execution completed",
                action=action,
                executed=True,
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr
            )
