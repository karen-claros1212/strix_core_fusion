import os
import re

from .sandbox_types import SandboxConfig, SandboxAction, RiskLevel, ValidationResult


class SandboxPolicy:
    def __init__(self, config: SandboxConfig = None):
        self.config = config or SandboxConfig()
        self.workspace_root = self.config.workspace_root
        self.blocked_paths = ["/var/run/docker.sock", "/etc/shadow", "/root/.ssh"]
        self.allowed_networks = self.config.allowed_networks if self.config and hasattr(self.config, "allowed_networks") else []
        self.blocked_networks = self.config.blocked_networks if self.config and hasattr(self.config, "blocked_networks") else []
        self.metadata_ips = ["169.254.169.254"]

    def _decision(self, allowed: bool, reason: str, severity: str, policy_id: str, errors: list[str] | None = None) -> ValidationResult:
        return ValidationResult({
            "allowed": allowed,
            "reason": reason,
            "severity": severity,
            "policy_id": policy_id,
            "errors": (errors or []),
            "details": {"errors": (errors or [])},
        })

    def validate_path(self, path: str) -> bool:
        """Validates if a path is within the workspace and not blocked."""
        if not path:
            return False
        try:
            abs_path = os.path.abspath(path)
        except ValueError:
            return False
        if not abs_path.startswith(self.workspace_root):
            return False
        if ".." in path:
            return False
        for blocked in self.blocked_paths:
            if abs_path == os.path.abspath(blocked):
                return False
        return True

    def validate_filesystem(self, path: str, workspace: str) -> dict:
        """Validates filesystem operations."""
        errors = []
        # Resolve path relative to workspace
        full_path = os.path.join(workspace, path) if not os.path.isabs(path) else path
        if not full_path.startswith(workspace):
            errors.append("Ruta fuera del workspace")
        if ".." in path:
            errors.append("Path traversal")
        allowed = len(errors) == 0
        return self._decision(allowed, "Valid" if allowed else "Invalid", "HIGH" if not allowed else "LOW", "FS_POLICY_001", errors)

    def validate_network(self, target: str) -> dict:
        """Validates if a network target is allowed."""
        if not target:
            return self._decision(True, "No target specified", "LOW", "NET_POLICY_001")
        errors = []
        # Check for metadata IPs and domains
        metadata_refs = self.metadata_ips + ["metadata.google.internal", "metadata"]
        for ref in metadata_refs:
            if target == ref or ref in target:
                errors.append("Metadata endpoint")
        if errors:
            return self._decision(False, "Invalid", "HIGH", "NET_POLICY_001", errors)
        # Check if known safe local/private IP
        import ipaddress
        try:
            ip_obj = ipaddress.ip_address(target)
            if ip_obj.is_loopback or ip_obj.is_private:
                return self._decision(True, "Valid", "LOW", "NET_POLICY_001")
        except ValueError:
            pass  # domain name
        return self._decision(True, "Valid", "LOW", "NET_POLICY_001")

    def validate_command(self, action: SandboxAction) -> dict:
        """Validates command risks."""
        errors = []
        if isinstance(action, str):
            cmd = action
            args = []
        else:
            cmd = action.command
            args = action.args
        all_tokens = cmd.split() + (args or [])
        # Check for dangerous commands
        if "docker" in all_tokens:
            errors.append("docker")
        if "kubectl" in all_tokens:
            errors.append("kubectl")
        # Check for rm -rf
        if "rm" in all_tokens and "-rf" in all_tokens:
            errors.append("rm -rf detected")
        # Check for privileged docker
        if "--privileged" in all_tokens:
            errors.append("Privileged docker detected")
        # Check for docker.sock
        if "docker.sock" in cmd:
            errors.append("docker.sock")
        # Check for path traversal
        if ".." in cmd:
            errors.append("Path traversal")
        # Check for blocked files (shadow, etc)
        for bp in self.blocked_paths:
            if bp in cmd:
                errors.append(bp)
        allowed = len(errors) == 0
        return self._decision(allowed, "Valid" if allowed else "Invalid", "HIGH" if not allowed else "LOW", "CMD_POLICY_001", errors)

    def is_allowed(self, action: SandboxAction) -> bool:
        """Check if action is allowed based on risk level and command."""
        if action.risk_level == RiskLevel.R5:
            return False
        return bool(self.validate_command(action))

    def is_allowed(self, action: SandboxAction) -> bool:
        """Check if action is allowed based on risk level and command."""
        if action.risk_level == RiskLevel.R5:
            return False
        return bool(self.validate_command(action))
