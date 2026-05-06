from typing import List, Dict, Any

class AgentState:
    """
    Clase base para el estado del agente en Strix.
    Maneja el historial de conversación y el estado actual.
    """
    def __init__(self):
        self.messages: List[Dict[str, Any]] = []
        self.history: List[Dict[str, Any]] = []
        self.context_window: int = 8192

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """
        Devuelve el historial de conversación actual.
        """
        return self.history if self.history else self.messages

    def update_history(self, new_messages: List[Dict[str, Any]]):
        """
        Actualiza el historial con nuevos mensajes.
        """
        self.history.extend(new_messages)
        self.messages.extend(new_messages)

    def clear_history(self):
        """
        Limpia el historial.
        """
        self.history.clear()
        self.messages.clear()
