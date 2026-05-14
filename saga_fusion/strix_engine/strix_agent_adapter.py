from __future__ import annotations

from strix.integrations.telegram import (
    StrixCoreGateway,
    StrixCoreGatewayResult,
    StrixTelegramAdapter,
    StrixTelegramAdapterResult,
)

# Backwards-compatible Saga Fusion wrapper. The canonical implementation lives
# in strix.integrations.telegram so STRIX Core remains the primary engine path.
StrixAgentAdapter = StrixTelegramAdapter
StrixAgentAdapterResult = StrixTelegramAdapterResult

__all__ = [
    "StrixAgentAdapter",
    "StrixAgentAdapterResult",
    "StrixTelegramAdapter",
    "StrixTelegramAdapterResult",
    "StrixCoreGateway",
    "StrixCoreGatewayResult",
]
