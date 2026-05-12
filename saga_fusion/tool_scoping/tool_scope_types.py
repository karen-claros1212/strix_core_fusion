from __future__ import annotations

from dataclasses import dataclass, field

from saga_fusion.tool_routing.tool_routing_types import ToolRisk


@dataclass(frozen=True)
class ToolScope:
    """Declarative allow/deny metadata for a non-executing toolset scope."""

    name: str
    category: str
    allowed_tools: tuple[str, ...]
    denied_tools: tuple[str, ...] = ()
    description: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", str(self.name or "").strip().lower())
        object.__setattr__(self, "category", str(self.category or "").strip().lower())
        object.__setattr__(self, "allowed_tools", tuple(_normalize_tool(tool) for tool in self.allowed_tools))
        object.__setattr__(self, "denied_tools", tuple(_normalize_tool(tool) for tool in self.denied_tools))
        object.__setattr__(self, "description", str(self.description or "").strip())


@dataclass(frozen=True)
class ToolLoopState:
    mission_id: str
    total_calls: int = 0
    repeated_calls: int = 0
    active_stack: tuple[str, ...] = ()
    call_signatures: tuple[str, ...] = ()


@dataclass(frozen=True)
class ToolLoopGuardConfig:
    max_tool_calls: int = 20
    max_repeated_tool_calls: int = 3


@dataclass(frozen=True)
class ToolScopeEvidence:
    scope_sources: tuple[str, ...] = ()
    allowed_tools: tuple[str, ...] = ()
    denied_tools: tuple[str, ...] = ()
    tool_name: str = "unknown"
    risk_level: ToolRisk = ToolRisk.R4
    metadata: dict = field(default_factory=dict)


def _normalize_tool(tool: str) -> str:
    return str(tool or "").strip().lower()


__all__ = ["ToolScope", "ToolLoopState", "ToolLoopGuardConfig", "ToolScopeEvidence"]
