from __future__ import annotations

from .tool_classifier import ToolClassifier
from .tool_registry import ToolRegistry
from .tool_route_policy import ToolRoutePolicy
from .tool_routing_types import ToolExecutionPlan


class ToolRouter:
    def __init__(self, registry: ToolRegistry | None = None, classifier: ToolClassifier | None = None, policy: ToolRoutePolicy | None = None):
        self.registry = registry or ToolRegistry()
        self.classifier = classifier or ToolClassifier(self.registry)
        self.policy = policy or ToolRoutePolicy(self.registry)
        self.executed = False

    def route_tool_request(self, request, context=None):
        classification = self.classifier.classify(request, context=context)
        return self.policy.decide(classification, request=request, context=context)

    def build_execution_plan(self, decision, request=None) -> ToolExecutionPlan:
        args = request if isinstance(request, dict) else {
            'action_type': getattr(request, 'action_type', ''),
            'target': getattr(request, 'target', ''),
            'arguments': getattr(request, 'arguments', ''),
        }
        return ToolExecutionPlan(
            tool_name=decision.tool_name,
            action=str(args.get('action') or args.get('action_type') or decision.tool_name),
            args=dict(args),
            risk_level=decision.risk_level,
            sandbox_mode='dry_run' if decision.sandbox_required else 'not_required',
            dry_run=True,
            approval_required=decision.approval_required,
            evidence_required=True,
            execution_allowed=decision.allowed and not decision.blocked and not decision.approval_required,
        )
