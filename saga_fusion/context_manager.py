import logging
from typing import List, Dict, Any, Optional

class SagaContextManager:
    """
    Gestiona el colapso de contexto (Mythos) de forma core-agnóstica.
    """
    def __init__(self, llm_config: Any = None):
        self.llm_config = llm_config
        self.logger = logging.getLogger("Saga.ContextManager")

    def get_context_window(self) -> int:
        """Detecta la ventana de contexto del modelo."""
        attrs = ['context_window', 'max_context_tokens', 'model_context_length', 'max_input_tokens', 'max_tokens']
        for attr in attrs:
            if hasattr(self.llm_config, attr):
                return getattr(self.llm_config, attr)
        return 8192 # Fallback seguro

    def collapse_history(self, history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Aplica la lógica de colapso de contexto.
        """
        if not history:
            return history

        # Estimación de tokens (simplificada: 1 token ~ 4 chars)
        estimated_tokens = sum(len(str(msg.get('content', ''))) // 4 for msg in history)
        max_tokens = self.get_context_window()
        soft_limit = max_tokens * 0.85
        hard_limit = max_tokens * 0.98

        if estimated_tokens > hard_limit:
            self.logger.warning("[MYTHOS] Hard Limit. Generando resumen.")
            return self._generate_summary(history)
        elif estimated_tokens > soft_limit:
            self.logger.info("[MYTHOS] Soft Limit. Aplicando poda.")
            return self._apply_pruning(history)

        return list(history)

    def _apply_pruning(self, history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Elimina mensajes antiguos preservando system y últimos user/tool."""
        system_msgs = [m for m in history if m.get('role') in ['system', 'developer', 'security']]
        recent_turns = []
        for m in reversed(history):
            if m.get('role') in ['user', 'assistant', 'tool']:
                recent_turns.append(m)
            if len(recent_turns) >= 6: # 3 turnos x 2 (user+assistant/tool)
                break
        return system_msgs + recent_turns

    def _generate_summary(self, history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Genera un bloque de resumen para mantener coherencia."""
        system_msgs = [m for m in history if m.get('role') in ['system', 'developer', 'security']]
        summary_msg = {
            "role": "assistant",
            "content": "[MYTHOS_SUMMARY] El contexto ha sido comprimido para optimizar tokens. Se mantiene la coherencia semántica de los últimos turnos."
        }
        return system_msgs + [summary_msg]
