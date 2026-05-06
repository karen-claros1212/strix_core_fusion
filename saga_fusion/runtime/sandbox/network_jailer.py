import ipaddress
from .sandbox_types import SandboxConfig, ValidationResult

class NetworkJailer:
    def __init__(self, config: SandboxConfig = None):
        self.config = config if config is not None else SandboxConfig()
        self.blocked_ips = [ipaddress.ip_address("169.254.169.254")] # AWS Metadata
        self.allowed_cidrs = [ipaddress.ip_network(net) for net in (self.config.allowed_networks if self.config else [])]
        self.blocked_cidrs = [ipaddress.ip_network(net) for net in (self.config.blocked_networks if self.config else [])]

    def validate_network(self, target: str) -> ValidationResult:
        """Validates if a network target is allowed."""
        if not target:
            return ValidationResult({"allowed": True, "details": {"reason": "empty target"}})
        try:
            ip = ipaddress.ip_address(target)
            if ip.is_loopback:
                return ValidationResult({"allowed": True, "details": {"reason": "loopback"}})
            # Check blocked IPs
            for blocked_ip in self.blocked_ips:
                if ip == blocked_ip:
                    return ValidationResult({"allowed": False, "details": {"reason": "metadata ip"}})
            for blocked_cidr in self.blocked_cidrs:
                if ip in blocked_cidr:
                    return ValidationResult({"allowed": False, "details": {"reason": "blocked cidr"}})
            # Check scope
            if not self.allowed_cidrs:
                return ValidationResult({"allowed": False, "details": {"reason": "external network blocked by default"}})
            in_allowed = any(ip in net for net in self.allowed_cidrs)
            return ValidationResult({"allowed": in_allowed, "details": {"reason": "allowed cidr" if in_allowed else "not in allowed cidrs"}})
        except ValueError:
            return ValidationResult({"allowed": False, "details": {"reason": "invalid target"}})
    def is_allowed(self, target: str) -> bool:
        return bool(self.validate_network(target))
