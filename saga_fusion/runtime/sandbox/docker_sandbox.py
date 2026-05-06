import subprocess
import os
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from saga_fusion.runtime.sandbox.sandbox_types import SandboxPlan, SandboxResult, RiskLevel
from saga_fusion.runtime.sandbox.sandbox_policy import SandboxPolicy
from saga_fusion.runtime.sandbox.sandbox_audit import SandboxAudit
from saga_fusion.runtime.evidence.evidence_store import SagaEvidenceStore

class DockerSandbox:
    """
    Implementación del Sandbox usando Docker.
    """
    
    def __init__(self, workspace: str, evidence_store: SagaEvidenceStore = None):
        self.workspace = workspace
        self.policy = SandboxPolicy()
        self.evidence_store = evidence_store or SagaEvidenceStore()
        self.audit = SandboxAudit(self.evidence_store)
        
    def is_available(self) -> bool:
        """Verifica si Docker está instalado y corriendo."""
        try:
            result = subprocess.run(["docker", "info"], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
            
    def execute(self, mission_id: str, command: str, limits: SandboxPlan = None) -> SandboxResult:
        """
        Ejecuta un comando en un contenedor Docker.
        """
        plan = limits or SandboxPlan(
            mission_id=mission_id,
            provider="docker",
            image="alpine:latest",
            command=command,
            limits=self.policy.DEFAULT_LIMITS,
            risk_level=self.policy.DEFAULT_LIMITS.risk_level
        )
        
        # 1. Validar Comando
        cmd_validation = self.policy.validate_command(command)
        if not cmd_validation["valid"]:
            return self._create_result(False, "", RiskLevel.BLOCKED, f"Comando bloqueado: {'; '.join(cmd_validation['errors'])}")
            
        # 2. Validar Redes
        net_validation = self.policy.validate_network(command)
        if not net_validation["valid"]:
            return self._create_result(False, "", RiskLevel.BLOCKED, f"Red error: {'; '.join(net_validation['errors'])}")
            
        # 3. Construir comandos Docker
        docker_cmd = [
            "docker", "run",
            "--rm", # Auto-eliminar al terminar
            "--name", f"strix-{mission_id[:8]}",
            "-v", f"{self.workspace}:/workspace:rw",
            "-w", "/workspace",
            "--memory", f"{plan.limits.memory_mb}m",
            "--cpus", f"{plan.limits.cpu_percent / 100}",
            "--network", "bridge",
            plan.image,
            "sh", "-c", command
        ]
        
        # 4. Ejecutar
        start_time = datetime.now(timezone.utc)
        try:
            result = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                timeout=plan.limits.timeout_seconds
            )
            
            output = result.stdout + result.stderr
            success = result.returncode == 0
            
            # 5. Registrar Evidence
            self.audit.log_execution(mission_id, command, success, output, plan)
            
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
            evidence_id="docker_exec", # Simplificado
            blocked_reason=blocked_reason
        )