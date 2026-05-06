import psutil
import os
from .sandbox_types import SandboxConfig

class ResourceLimiter:
    def __init__(self, config: SandboxConfig = None, cpu_limit: float = 1.0, memory_limit: float = 512.0):
        self.config = config if config is not None else SandboxConfig()
        self.cpu_limit = cpu_limit
        self.ram_limit_mb = memory_limit
        self.timeout_seconds = self.config.timeout_seconds
    def validate_resources(self, current_pid: int) -> bool:
        """Check if current process is within limits."""
        try:
            process = psutil.Process(current_pid)
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / (1024 * 1024)
            
            if memory_mb > self.ram_limit_mb:
                return False
            
            # CPU check (simple heuristic)
            cpu_percent = process.cpu_percent(interval=0.1)
            # Assuming 100% is one core, limit is in cores
            if cpu_percent > (self.cpu_limit * 100):
                return False
                
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return True # Assume OK if we can't check

    def get_timeout(self) -> int:
        return self.timeout_seconds

    def is_allowed(self, cpu_usage: float = 0.0, memory_usage: float = 0.0) -> bool:
        """Check if resource usage is within limits."""
        if cpu_usage > self.cpu_limit:
            return False
        if memory_usage > self.ram_limit_mb:
            return False
        return True
