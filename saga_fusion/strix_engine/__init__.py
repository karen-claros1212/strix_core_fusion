"""Optional adapters for invoking the real STRIX engine from Saga Fusion."""

from .strix_agent_adapter import StrixAgentAdapter, StrixAgentAdapterResult

__all__ = ["StrixAgentAdapter", "StrixAgentAdapterResult"]
