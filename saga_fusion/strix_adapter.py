import logging
from typing import List, Dict, Any, Optional

# Importaciones de Strix Base
try:
        from strix.agents.unified_saga_agent import UnifiedSagaAgent as BaseAgent
        from strix.agents.state import AgentState
except ImportError:
    logging.error("Strix base not found in PYTHONPATH.")
    raise

# Importaciones Saga Fusion
from saga_fusion.context_manager import SagaContextManager
from saga_fusion.tool_guard import SagaToolGuard
from saga_fusion.security_policy import SagaSecurityPolicy
from saga_fusion.audit_logger import SagaAuditLogger
from saga_fusion.evidence.evidence_store import SagaEvidenceStore
from saga_fusion.runtime.output_budget import SagaOutputBudget
from saga_fusion.runtime.process_guard import SagaProcessGuard

class StrixSagaAgent(BaseAgent):
    """
    Adaptador oficial para Strix + Saga Fusion Middleware.
    Hereda de BaseAgent sin modificar su implementación interna.
    """
    def __init__(self, *args, **kwargs):
        # Inicializar state antes de llamar a super() para evitar NoneType
        self.state = kwargs.get('state') or AgentState()
        kwargs.pop('state', None) # Limpiar kwargs para evitar duplicado
        super().__init__(state=self.state, *args, **kwargs) # Eliminar llamada duplicada
        self.state = self.state # Restaurar state después de que super() lo resetee a None
        
        
        
        
        
        
        # Inicialización de Módulos Saga
        self.context_manager = SagaContextManager(getattr(self, 'llm', None))
        self.security_policy = SagaSecurityPolicy()
        self.audit_logger = SagaAuditLogger()
        self.context_manager = SagaContextManager(getattr(self, 'llm', None))
        
        # Inyección de módulos Fase 4
        self.evidence_store = SagaEvidenceStore()
        self.output_budget = SagaOutputBudget(evidence_store=self.evidence_store)
        self.process_guard = SagaProcessGuard(evidence_store=self.evidence_store, output_budget=self.output_budget)
        
        self.tool_guard = SagaToolGuard(self.security_policy, self.audit_logger)

    async def _execute_actions(self, actions: List[Dict[str, Any]]) -> bool:
        """
        Intercepta acciones antes de ejecución.
        """
        if not actions:
            return await super()._execute_actions(actions)

        # 1. Evaluar acciones con ToolGuard
        allowed_actions, denied_results = self.tool_guard.evaluate_actions(actions)

        # 2. Loguear resultados denegados
        for result in denied_results:
            self.logger.warning(f"[SEC] Acción denegada: {result['reason']}")

        # 3. Ejecutar solo permitidas (o todas si el executor original maneja denegadas)
        # Asumimos que pasamos las permitidas al executor original
        if not allowed_actions:
            self.logger.info("[SEC] No hay acciones permitidas. Saltando ejecución.")
            return False

        return await super()._execute_actions(allowed_actions)

    async def _process_iteration(self):
        """
        Intercepta el bucle antes de llamar al LLM para colapsar contexto.
        """
        # 1. Colapsar contexto si es necesario
        current_history = self.state.get_conversation_history()
        compressed_history = self.context_manager.collapse_history(current_history)
        
        # 2. Actualizar estado (si el colapso modificó la lista)
        if compressed_history != current_history:
            self.state.messages = compressed_history
            self.logger.info("[MYTHOS] Contexto colapsado y estado actualizado.")

        # 3. Llamar al proceso original
        await super()._process_iteration()
