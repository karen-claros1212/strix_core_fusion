from __future__ import annotations

from .tool_registry import ToolRegistry
from .tool_routing_types import ToolCategory, ToolRisk, ToolRouteDecision


class ToolRoutePolicy:
    def __init__(self, registry: ToolRegistry | None = None):
        self.registry = registry or ToolRegistry()

    def decide(self, classification: dict, request=None, context=None) -> ToolRouteDecision:
        tool_name = classification.get('tool_name','unknown')
        tool = self.registry.get(tool_name)
        category = classification.get('category') or (tool.category if tool else ToolCategory.UNKNOWN)
        risk = classification.get('risk_level') or (tool.default_risk if tool else ToolRisk.R4)
        sandbox_required = bool(tool.requires_sandbox if tool else True)
        evidence = {'matched': classification.get('matched'), 'category': category.value, 'tool_name': tool_name}
        if tool is None or category == ToolCategory.UNKNOWN:
            return ToolRouteDecision(False, True, False, ToolRisk.R4, tool_name, ToolCategory.UNKNOWN, 'blocked', True, 'unknown_tool_blocked', evidence)
        if risk == ToolRisk.R5:
            return ToolRouteDecision(False, True, False, risk, tool.name, category, 'blocked', sandbox_required, 'risk_r5_blocked', evidence)
        if risk == ToolRisk.R4 or tool.requires_approval:
            return ToolRouteDecision(False, False, True, risk, tool.name, category, 'approval_required', sandbox_required, 'risk_r4_requires_approval', evidence)
        route = 'sandbox' if sandbox_required else 'direct_safe_metadata_only'
        return ToolRouteDecision(True, False, False, risk, tool.name, category, route, sandbox_required, 'allowed_by_tool_route_policy', evidence)
