from typing import List, Dict, Any, Optional
import logging

class BaseAgent:
    """
    Clase base mínima para Strix.
    Proporciona la estructura necesaria para la compatibilidad de Saga Fusion.
    """
    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.state = None
        self.config = {}

    def agent_loop(self, *args, **kwargs):
        """Método stub para el bucle principal."""
        pass

    def _process_iteration(self, *args, **kwargs):
        """Método stub para procesar iteraciones."""
        pass

    def _execute_actions(self, actions: List[Dict[str, Any]]) -> List[Any]:
        """Método stub para ejecutar acciones."""
        return []

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Método stub para obtener el historial."""
        return []