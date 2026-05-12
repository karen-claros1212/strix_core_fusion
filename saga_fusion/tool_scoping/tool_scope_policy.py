from __future__ import annotations

from collections.abc import Iterable

from saga_fusion.tool_routing.tool_classifier import ToolClassifier
from saga_fusion.tool_routing.tool_registry import ToolRegistry
from saga_fusion.tool_routing.tool_routing_types import ToolCategory, ToolRisk, ToolRouteDecision

from .toolset_scope_registry import ToolsetScopeRegistry


class ToolScopePolicy:
    """Mission/workflow/skill tool scoping gate before ToolRouter decisions."""

    def __init__(self, registry: ToolRegistry | None = None, classifier: ToolClassifier | None = None, toolsets: ToolsetScopeRegistry | None = None):
        self.registry = registry or ToolRegistry()
        self.classifier = classifier or ToolClassifier(self.registry)
        self.toolsets = toolsets or ToolsetScopeRegistry()

    def decide(self, request, context: dict | None = None, classification: dict | None = None) -> ToolRouteDecision:
        context = dict(context or {})
        classification = dict(classification or self.classifier.classify(request, context=context))
        tool_name = str(classification.get("tool_name") or self._explicit_tool(request) or "unknown").strip().lower()
        tool = self.registry.get(tool_name)
        category = classification.get("category") or (tool.category if tool else ToolCategory.UNKNOWN)
        risk = classification.get("risk_level") or (tool.default_risk if tool else ToolRisk.R4)
        sandbox_required = bool(tool.requires_sandbox if tool else True)
        allowed, denied, sources, skill_widen_attempt = self._effective_scope(context)
        evidence = {
            "tool_name": tool_name,
            "matched": classification.get("matched"),
            "scope_sources": sorted(sources),
            "allowed_tools": sorted(allowed),
            "denied_tools": sorted(denied),
            "metadata_only": True,
            "execution_allowed": False,
        }
        dangerous = classification.get("dangerous_action")
        if dangerous is not None:
            evidence["dangerous_action"] = {
                "reason": dangerous.reason,
                "categories": [item.value for item in dangerous.categories],
                "severity": dangerous.severity.value,
            }

        if skill_widen_attempt:
            evidence["skill_requested_allowed_tools"] = sorted(skill_widen_attempt)
            return ToolRouteDecision(False, True, False, ToolRisk.R4, tool_name, ToolCategory.UNKNOWN, "blocked", True, "skill_cannot_widen_own_scope", evidence)
        if tool is None or category == ToolCategory.UNKNOWN or tool_name == "unknown":
            return ToolRouteDecision(False, True, False, ToolRisk.R4, tool_name, ToolCategory.UNKNOWN, "blocked", True, "unknown_tool_blocked", evidence)
        if tool_name in denied:
            return ToolRouteDecision(False, True, False, risk, tool.name, category, "blocked", sandbox_required, "denied_tool_blocked", evidence)
        if allowed and tool_name not in allowed:
            return ToolRouteDecision(False, True, False, risk, tool.name, category, "blocked", sandbox_required, "out_of_scope_tool_blocked", evidence)
        if risk == ToolRisk.R5:
            return ToolRouteDecision(False, True, False, risk, tool.name, category, "blocked", sandbox_required, "risk_r5_blocked", evidence)
        if risk == ToolRisk.R4 or tool.requires_approval:
            return ToolRouteDecision(False, False, True, risk, tool.name, category, "approval_required", sandbox_required, "risk_r4_requires_approval", evidence)
        return ToolRouteDecision(True, False, False, risk, tool.name, category, "scope_allowed", sandbox_required, "allowed_by_tool_scope_policy", evidence)

    def _effective_scope(self, context: dict) -> tuple[set[str], set[str], set[str], set[str]]:
        allowed_sets: list[set[str]] = []
        denied: set[str] = set()
        sources: set[str] = set()

        mission_id = str(context.get("mission_id") or "").strip()
        mission_scopes = context.get("mission_tool_scopes") or context.get("mission_allowed_tools_by_id") or {}
        if mission_id and isinstance(mission_scopes, dict) and mission_id in mission_scopes:
            allowed_sets.append(self._normalize_tools(mission_scopes[mission_id]))
            sources.add(f"mission:{mission_id}")
        if context.get("mission_allowed_tools") is not None:
            allowed_sets.append(self._normalize_tools(context.get("mission_allowed_tools")))
            sources.add("mission")

        workflow = str(context.get("workflow") or context.get("workflow_id") or "").strip().lower()
        workflow_scopes = context.get("workflow_tool_scopes") or context.get("workflow_allowed_tools_by_id") or {}
        if workflow and isinstance(workflow_scopes, dict) and workflow in workflow_scopes:
            allowed_sets.append(self._normalize_tools(workflow_scopes[workflow]))
            sources.add(f"workflow:{workflow}")
        if context.get("workflow_allowed_tools") is not None:
            allowed_sets.append(self._normalize_tools(context.get("workflow_allowed_tools")))
            sources.add("workflow")

        toolset_names = context.get("toolsets") or context.get("toolset")
        if toolset_names is not None:
            toolset_allowed = self.toolsets.allowed_tools_for(toolset_names)
            toolset_denied = self.toolsets.denied_tools_for(toolset_names)
            allowed_sets.append(toolset_allowed)
            denied.update(toolset_denied)
            sources.add("toolset")

        skill_allowed = self._skill_allowed_tools(context)
        if skill_allowed is not None:
            allowed_sets.append(skill_allowed)
            sources.add("skill")

        requested_skill_scope = self._optional_tool_set(context.get("skill_requested_allowed_tools") or context.get("skill_scope_request"))
        skill_widen_attempt: set[str] = set()
        if requested_skill_scope is not None and skill_allowed is not None:
            skill_widen_attempt = requested_skill_scope - skill_allowed

        denied.update(self._normalize_tools(context.get("denied_tools") or ()))
        if context.get("allowed_tools") is not None:
            allowed_sets.append(self._normalize_tools(context.get("allowed_tools")))
            sources.add("context")

        if not allowed_sets:
            return set(), denied, sources, skill_widen_attempt
        effective = set(allowed_sets[0])
        for tools in allowed_sets[1:]:
            effective.intersection_update(tools)
        effective.difference_update(denied)
        return effective, denied, sources, skill_widen_attempt

    @staticmethod
    def _skill_allowed_tools(context: dict) -> set[str] | None:
        manifest = context.get("skill_manifest") or context.get("skill")
        if manifest is None:
            return None
        allowed_tools = getattr(manifest, "allowed_tools", None)
        if allowed_tools is None and isinstance(manifest, dict):
            allowed_tools = manifest.get("allowed_tools")
        return ToolScopePolicy._optional_tool_set(allowed_tools)

    @staticmethod
    def _optional_tool_set(values) -> set[str] | None:
        if values is None:
            return None
        return ToolScopePolicy._normalize_tools(values)

    @staticmethod
    def _normalize_tools(values) -> set[str]:
        if values is None:
            return set()
        if isinstance(values, str):
            values = (values,)
        if not isinstance(values, Iterable):
            values = (values,)
        return {str(value or "").strip().lower() for value in values if str(value or "").strip()}

    @staticmethod
    def _explicit_tool(request) -> str:
        if isinstance(request, dict):
            return str(request.get("tool_name") or "").strip().lower()
        return str(getattr(request, "tool_name", "") or "").strip().lower()


__all__ = ["ToolScopePolicy"]
