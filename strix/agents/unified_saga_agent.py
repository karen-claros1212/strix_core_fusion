import asyncio
import logging
import re
from typing import List, Dict, Any

# Importaciones dinámicas del core base de Strix
try:
    from strix.agents.base_agent import BaseAgent
    from strix.agents.state import AgentState
except ImportError:
    logging.error("Directorio strix_base no encontrado en el PYTHONPATH.")
    raise

class UnifiedSagaAgent(BaseAgent):
    """
    Motor Híbrido: Orquestación Strix (Apache 2.0) + Memoria Mythos + Contención CAI.
    Arquitectura estrictamente core-agnóstica.
    """
    def __init__(self, *args, **kwargs):
        self._saved_state = kwargs.pop('state', None)
        super().__init__(*args, **kwargs)
        if self._saved_state:
            self.state = self._saved_state
        self._setup_fusion_hooks()
        self.logger = logging.getLogger("SagaUnifiedCore")

    def _setup_fusion_hooks(self):
        """
        Inyecta los módulos interceptando los métodos de Strix en tiempo de ejecución.
        """
        # Hook A: Mythos Context Collapse (Gestión de Memoria)
        self._original_get_history = self.state.get_conversation_history
        self.state.get_conversation_history = self._hook_context_collapse

        # Hook B: CAI Security Wrappers (Sanitización de Herramientas)
        self._original_execute_actions = self._execute_actions
        self._execute_actions = self._hook_secure_execution

    def _hook_context_collapse(self) -> List[Dict[str, Any]]:
        """
        Fase 3.2 de Mythos: Prevención de desbordamiento de tokens mediante poda dinámica.
        """
        history = self._original_get_history()
        
        # Estimación core-agnóstica de tokens (1 token ~= 4 caracteres para portabilidad)
        estimated_tokens = sum(len(str(msg.get('content', ''))) // 4 for msg in history)
        
        # Obtenemos el límite del LLConfig de Strix. Si no existe, usamos un default seguro.
        max_context = getattr(self.llm.config, 'max_tokens', 8192)
        soft_limit = max_context * 0.85
        hard_limit = max_context * 0.98

        if estimated_tokens > hard_limit:
            self.logger.warning("[MYTHOS] Hard Limit alcanzado. Ejecutando poda de emergencia.")
            # Recorte estricto: conservamos el system prompt (índice 0) y los últimos 5 mensajes
            history = [history[0]] + history[-5:]
            self.state.messages = history # Sincronizar estado base
            
        elif estimated_tokens > soft_limit:
            self.logger.info("[MYTHOS] Soft Limit alcanzado. Aplicando poda cronológica (snipOldest).")
            # Poda cronológica básica: eliminamos mensajes antiguos preservando el prompt inicial
            history = [history[0]] + history[3:]
            self.state.messages = history
            
        return history

    async def _hook_secure_execution(self, actions=None):
        """
        Fase B (CAI): Intercepta las acciones generadas por el LLM antes de ejecutarlas.
        Aplica los filtros regex y verifica comandos peligrosos.
        """
        # 1. Recuperamos las acciones pendientes (lógica interna de Strix)
        if not actions:
            actions = self._current_actions if hasattr(self, '_current_actions') else []
        if not actions:
            return await self._original_execute_actions()
            return await self._original_execute_actions()

        sanitized_actions = []
        for action in self._current_actions:
            cmd = action.get('command', '')
            
            # 2. Sanitizador Paranoico (Inspirado en Mythos Fase 5 y CAI)
            if self._detect_shell_injection(cmd):
                self.logger.critical(f"[CAI SEC-BLOCK] Intento de inyección de shell detectado: {cmd}")
                # Mutamos la acción para devolver un error al agente en lugar de ejecutarla
                action['command'] = "echo '[CAI] Ejecución denegada por violación de políticas de seguridad.'"
            else:
                action['command'] = self._sanitize_paths(cmd)
                
            sanitized_actions.append(action)

        self._current_actions = sanitized_actions
        
        # 3. Continuar con la ejecución original usando las acciones sanitizadas
        return await self._original_execute_actions()

    def _detect_shell_injection(self, command: str) -> bool:
        """Filtro de contención estática para comandos bash y vim."""
        dangerous_patterns = [
            r'>\s*/dev/(tcp|udp)',  # Reverse shells
            r'rm\s+-rf\s+/',        # Borrado recursivo crítico
            r'!\s*bash',            # VimTool shell escape
            r'mkfifo'               # Named pipes para exfiltración
        ]
        for pattern in dangerous_patterns:
            if re.search(pattern, command):
                return True
        return False

    def _sanitize_paths(self, output: str) -> str:
        """Oculta rutas críticas del sistema anfitrión."""
        return re.sub(r'/home/[^/]+/\.ssh/.*', '[REDACTED_SSH_KEY]', output)
