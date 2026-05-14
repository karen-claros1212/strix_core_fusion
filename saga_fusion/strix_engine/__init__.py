"""Compatibility wrappers for STRIX Core integrations used by Saga Fusion."""

from .strix_agent_adapter import (
    StrixAgentAdapter,
    StrixAgentAdapterResult,
    StrixCoreGateway,
    StrixCoreGatewayResult,
    StrixTelegramAdapter,
    StrixTelegramAdapterResult,
)

__all__ = [
    "StrixAgentAdapter",
    "StrixAgentAdapterResult",
    "StrixTelegramAdapter",
    "StrixTelegramAdapterResult",
    "StrixCoreGateway",
    "StrixCoreGatewayResult",
]
