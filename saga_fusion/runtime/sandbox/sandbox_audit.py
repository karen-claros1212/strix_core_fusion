import json
import os
from datetime import datetime, timezone
from pathlib import Path
from .sandbox_types import SandboxConfig, SandboxAction, SandboxResult

class SandboxAudit:
    def __init__(self, config: SandboxConfig, evidence_store=None):
        self.config = config
        self.evidence_store = evidence_store
        self.mission_id = "sandbox_local_session"
        self.audit_log_path = Path(config.workspace_root) / "evidence" / "missions" / self.mission_id / "sandbox_audit.jsonl"
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)

    def log_action(self, action: SandboxAction, result: SandboxResult):
        """Log action and result to JSONL file."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": {
                "command": action.command,
                "args": action.args,
                "risk_level": action.risk_level.value,
                "workspace_path": action.workspace_path
            },
            "result": {
                "success": result.success,
                "message": result.message,
                "exit_code": result.exit_code
            }
        }
        
        with open(self.audit_log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def save_raw_output(self, action: SandboxAction, stdout: str, stderr: str):
        """Save raw output to evidence store if available."""
        if self.evidence_store:
            artifact_name = f"sandbox_{action.command.replace('/', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            content = f"STDOUT:\n{stdout}\n\nSTDERR:\n{stderr}"
            self.evidence_store.write_raw_output(
                self.mission_id,
                artifact_name,
                content
            )
    def __init__(self, config: SandboxConfig = None, evidence_store=None):
        self.config = config or SandboxConfig()
        self.evidence_store = evidence_store
        self.mission_id = "sandbox_local_session"
        self.logs = []
    def log_action(self, action: SandboxAction, result):
        """Log action and result to JSONL file."""
        # Handle dict result
        if isinstance(result, dict):
            success = result.get('success', False)
            message = result.get('message', '')
            exit_code = result.get('exit_code', 0)
        else:
            success = result.success
            message = result.message
            exit_code = result.exit_code

        self.logs.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": {
                "command": action.command,
                "args": action.args,
                "risk_level": action.risk_level.value,
                "workspace_path": action.workspace_path
            },
            "result": {
                "success": success,
                "message": message,
                "exit_code": exit_code
            }
        })
