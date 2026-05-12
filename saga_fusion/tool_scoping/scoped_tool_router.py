from __future__ import annotations

from saga_fusion.tool_routing.tool_registry import ToolRegistry
from saga_fusion.tool_routing.tool_router import ToolRouter
from saga_fusion.tool_routing.tool_routing_types import ToolExecutionPlan

from .tool_loop_guard import ToolLoopGuard
from .tool_scope_policy import ToolScopePolicy


class ScopedToolRouter:
    """Scope + loop guarded wrapper around ToolRouter. It never executes tools."""

    def __init__(self, tool_router: ToolRouter | None = None, scope_policy: ToolScopePolicy | None = None, loop_guard: ToolLoopGuard | None = None):
        self.tool_router = tool_router or ToolRouter()
        self.registry: ToolRegistry = self.tool_router.registry
        self.scope_policy = scope_policy or ToolScopePolicy(registry=self.registry, classifier=self.tool_router.classifier)
        self.loop_guard = loop_guard or ToolLoopGuard()
        self.executed = False

    def route_tool_request(self, request, context: dict | None = None):
        context = dict(context or {})
        classification = self.tool_router.classifier.classify(request, context=context)
        scoped_decision = self.scope_policy.decide(request, context=context, classification=classification)
        if scoped_decision.blocked or scoped_decision.approval_required:
            return scoped_decision
        loop_decision = self.loop_guard.check(scoped_decision.tool_name, args=self._args(request), context=context)
        if loop_decision is not None:
            return loop_decision
        return self.tool_router.policy.decide(classification, request=request, context=context)

    def build_execution_plan(self, decision, request=None) -> ToolExecutionPlan:
        plan = self.tool_router.build_execution_plan(decision, request=request)
        return ToolExecutionPlan(
            tool_name=plan.tool_name,
            action=plan.action,
            args=plan.args,
            risk_level=plan.risk_level,
            sandbox_mode=plan.sandbox_mode,
            dry_run=True,
            approval_required=plan.approval_required,
            evidence_required=True,
            execution_allowed=False,
        )

    @staticmethod
    def _args(request) -> dict:
        if isinstance(request, dict):
            return dict(request)
        return {
            "tool_name": getattr(request, "tool_name", ""),
            "action_type": getattr(request, "action_type", ""),
            "target": getattr(request, "target", ""),
            "arguments": getattr(request, "arguments", ""),
        }


__all__ = ["ScopedToolRouter"]
