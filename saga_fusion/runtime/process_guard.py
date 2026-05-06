import subprocess
import signal
import os
from typing import Optional, Dict, Any
from datetime import datetime, timezone

from saga_fusion.runtime.output_budget import SagaOutputBudget
from saga_fusion.audit_logger import SagaAuditLogger

class SagaProcessGuard:
    def __init__(self, evidence_store=None, output_budget: SagaOutputBudget = None):
        self.evidence_store = evidence_store
        self.output_budget = output_budget or SagaOutputBudget()
        self.logger = SagaAuditLogger()
        self.default_timeout = 60
        self.max_timeout = 300
        self.kill_on_timeout = True

    def run_command(self, command: str, timeout: int = None, mission_id: str = "default_local_session") -> Dict[str, Any]:
        timeout = timeout or self.default_timeout
        timeout = min(timeout, self.max_timeout)
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return self._process_result(result, command, mission_id)
        except subprocess.TimeoutExpired:
            return self._handle_timeout(command, mission_id)

    def _process_result(self, result: subprocess.CompletedProcess, command: str, mission_id: str) -> Dict[str, Any]:
        stdout = result.stdout
        stderr = result.stderr
        
        # Redact secrets
        stdout = self.logger.redact_secrets(stdout)
        stderr = self.logger.redact_secrets(stderr)
        
        # Split for evidence and model view
        raw_stdout, model_stdout = self.output_budget.split_raw_and_model_view(
            stdout, mission_id, f"stdout_{command[:10]}"
        )
        
        return {
            "exit_code": result.returncode,
            "stdout": model_stdout,
            "stderr": stderr,
            "raw_stdout": raw_stdout,
            "timed_out": False
        }

    def _handle_timeout(self, command: str, mission_id: str) -> Dict[str, Any]:
        error_msg = f"Command timed out after {self.max_timeout}s: {command}"
        
        # Log timeout in evidence
        if self.evidence_store:
            self.evidence_store.append_command(mission_id, {
                "command": command,
                "error": error_msg,
                "type": "TIMEOUT"
            })
            
        return {
            "exit_code": -1,
            "stdout": "[TIMEOUT]",
            "stderr": error_msg,
            "raw_stdout": "[TIMEOUT]",
            "timed_out": True
        }
