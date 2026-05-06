import subprocess
import time
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from saga_fusion.runtime.sandbox.sandbox_types import SandboxPlan, SandboxResult, RiskLevel
from saga_fusion.runtime.sandbox.sandbox_policy import SandboxPolicy
from saga_fusion.runtime.sandbox.filesystem_jailer import FilesystemJailer
from saga_fusion.runtime.sandbox.network_jailer import NetworkJailer
from saga_fusion.runtime.sandbox.resource_limiter import ResourceLimiter
from saga_fusion.runtime.evidence.evidence_store import SagaEvidenceStore

class LocalSandbox:
    """
    Implementación del Sandbox usando subprocess y límites de recursos.
    """
    
    def __init__(self, workspace: str, evidence_store: SagaEvidenceStore = None):
        self.workspace = workspace
        self.policy = SandboxPolicy()
        self.filesystem_jailer = FilesystemJailer()
        self.network_jailer = NetworkJailer()
        self.resource_limiter = ResourceLimiter()
        self.evidence_store = evidence_store or SagaEvidenceStore()
        
    def execute(self, mission_id: str, command: str, limits: SandboxPlan = None) -> SandboxResult:
        """
        Ejecuta un comando en el sandbox local.
        """
        plan = limits or SandboxPlan(
            mission_id=mission_id,
            provider="local",
            image="alpine:latest",
            command=command,
            limits=Self.policy.DEFAULT_LIMITS,
            risk_level=Self.policy.DEFAULT_LIMITS.risk_level
        )
        
        # 1. Validar Comando
        cmd_validation = self.policy.validate_command(command)
        if not cmd_validation["valid"]:
            return self._create_result(False, "", RiskLevel.BLOCKED, f"Comando bloqueado: {'; '.join(cmd_validation['errors'])}")
        
        # 2. Validar Filesystem (si el comando toca archivos)
        fs_validation = self.policy.validate_filesystem(command, self.workspace)
        if not fs_validation["valid"]:
            return self._create_result(False, "", RiskLevel.BLOCKED, f"Filesystem error: {'; '.join(fs_validation['errors'])}")
            
        # 3. Aplicar Recursos
        self.resource_limiter.apply_limits(
            cpu_percent=plan.limits.cpu_percent,
            memory_mb=plan.limits.memory_mb
        )
        
        # 4. Ejecutar con Timeout
        start_time = time.time()
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=plan.limits.timeout_seconds,
                cwd=self.workspace
            )
            
            output = result.stdout + result.stderr
            success = result.returncode == 0
            
            # 5. Registrar Evidence
            self._log_execution(mission_id, command, success, output, plan)
            
            return self._create_result(success, output, plan.risk_level)
            
        except subprocess.TimeoutExpired:
            return self._create_result(False, "Timeout", RiskLevel.HIGH, "Timeout excedido")
        except Exception as e:
            return self._create_result(False, str(e), RiskLevel.HIGH, f"Error de ejecución: {str(e)}")
            
    def _create_result(self, success: bool, output: str, risk_level: RiskLevel, blocked_reason: str = None) -> SandboxResult:
        return SandboxResult(
            success=success,
            output=output,
            risk_level=risk_level,
            evidence_id="sandbox_exec", # Simplificado
            blocked_reason=blocked_reason
        )
        
    def _log_execution(self, mission_id: str, command: str, success: bool, output: str, plan: SandboxPlan):
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "mission_id": mission_id,
            "command": command,
            "success": success,
            "output": output,
            "risk_level": plan.risk_level.value,
            "workspace": self.workspace
        }
        # Guardar en evidence_store si existe
        if self.evidence_store:
            self.evidence_store.append_action(mission_id, record)