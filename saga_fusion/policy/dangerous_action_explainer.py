from __future__ import annotations

from .dangerous_action_types import DangerousActionDecision


class DangerousActionExplainer:
    def explain(self, decision: DangerousActionDecision) -> str:
        if not decision.detected:
            return 'No dangerous action detected; continue through normal MissionPolicy.'
        cats = ', '.join(category.value for category in decision.categories)
        if decision.blocked:
            outcome = 'blocked as R5 because it could cause destructive, exfiltrating, or policy-bypass impact'
            next_step = 'Use a dry-run audit/report plan or request a non-destructive review instead.'
        elif decision.approval_required:
            outcome = 'requires R4 approval before any execution path'
            next_step = 'Proceed only with approval workflow, dry-run plan, sandbox boundary, and evidence logging.'
        else:
            outcome = 'allowed for normal policy handling'
            next_step = 'Continue through MissionPolicy.'
        return f'Detected {cats}; {outcome}. Safe alternative: {next_step}'
