import logging
from typing import List, Dict, Any, Tuple
from saga_fusion.security_policy import SagaSecurityPolicy
from saga_fusion.audit_logger import SagaAuditLogger

class SagaToolGuard:
    """
    Intercepta acciones, evalúa política de seguridad y filtra resultados.
    """
    def __init__(self, policy: SagaSecurityPolicy = None, logger: SagaAuditLogger = None):
        self.policy = policy or SagaSecurityPolicy()
        self.logger = logger or SagaAuditLogger()

    def evaluate_actions(self, actions: List[Dict[str, Any]], executor=None) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Evalúa una lista de acciones.
        Retorna: (acciones_permitidas, resultados_denegados)
        """
        allowed_actions = []
        denied_results = []

        for action in actions:
            decision = self.policy.evaluate_action(action)
            self.logger.log_action(
                policy_id="tool_guard_01",
                action_type=action.get('type', 'unknown'),
                decision=decision,
                command=action.get('command', '')
            )

            if decision.allowed:
                allowed_actions.append(decision.sanitized_action)
            else:
                denied_results.append({
                    "type": "TOOL_RESULT",
                    "status": "DENIED",
                    "reason": decision.reason,
                    "severity": decision.severity,
                    "command_hash": decision.redacted_fingerprint,
                    "command": action.get('command', ''),
                    "action": action
                })

        return allowed_actions, denied_results
