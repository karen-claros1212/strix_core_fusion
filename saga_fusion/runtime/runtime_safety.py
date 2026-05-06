import re
import os
from typing import Optional, Dict, Any

class SagaRuntimeSafety:
    def __init__(self, workspace_root: str = None):
        self.workspace_root = workspace_root or os.getcwd()
        self.default_timeout = 60
        self.max_timeout = 300

    def validate_working_directory(self, path: str) -> bool:
        return path.startswith(self.workspace_root)

    def validate_file_operation(self, path: str, operation: str = "read") -> bool:
        # Prevent path traversal
        if ".." in path:
            return False
        
        # Prevent reading sensitive files
        if path in ["~/.ssh/id_rsa", "~/.ssh/id_ed25519", ".env"]:
            return False
        
        # Prevent dangerous write operations
        if operation == "write" and path == "/etc/passwd":
            return False
            
        return True

    def validate_network_target(self, target: str, scope: list = None) -> bool:
        # Basic validation for network targets
        if scope and target not in scope:
            return False
        return True

    def classify_runtime_action(self, action: str) -> str:
        if action.startswith("rm -rf"):
            return "DANGEROUS_DELETE"
        elif action.startswith("sudo"):
            return "ELEVATED_PRIVILEGE"
        elif action.startswith("curl") or action.startswith("wget"):
            return "NETWORK"
        else:
            return "SAFE"

    def enforce_timeout(self, command: str, timeout: int = None) -> int:
        if timeout is None:
            return self.default_timeout
        return min(timeout, self.max_timeout)
