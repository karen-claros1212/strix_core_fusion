from __future__ import annotations

from .memory_policy import MemoryPolicy
from .memory_types import ContextItem, MemoryScope, MemorySensitivity


class ContextWindow:
    def __init__(self, char_budget: int = 2000, policy: MemoryPolicy | None = None):
        self.char_budget = max(0, int(char_budget))
        self.policy = policy or MemoryPolicy()

    def _rank(self, item: ContextItem) -> tuple[int, str]:
        scope_bonus = {
            MemoryScope.PROJECT: 40,
            MemoryScope.MISSION: 35,
            MemoryScope.USER_APPROVED: 25,
            MemoryScope.SESSION: 10,
        }.get(item.scope, 0)
        text = f"{item.reason} {item.content}".lower()
        evidence_bonus = 20 if "evidence" in text or "report" in text else 0
        approval_bonus = 15 if item.user_approved or "approved" in text else 0
        constraint_bonus = 25 if "constraint" in text or "missionpolicy" in text or "promptsecurity" in text else 0
        return (item.priority + scope_bonus + evidence_bonus + approval_bonus + constraint_bonus, item.created_at)

    def select(self, items: list[ContextItem] | tuple[ContextItem, ...], char_budget: int | None = None) -> list[ContextItem]:
        budget = self.char_budget if char_budget is None else max(0, int(char_budget))
        candidates = [i for i in items if i.sensitivity != MemorySensitivity.SECRET_BLOCKED and self.policy.can_include(i).allowed]
        candidates.sort(key=self._rank, reverse=True)
        selected: list[ContextItem] = []
        used = 0
        for item in candidates:
            cost = len(item.content)
            sep = 1 if selected else 0
            if used + sep + cost > budget:
                continue
            selected.append(item)
            used += sep + cost
        return selected

    def render(self, items: list[ContextItem] | tuple[ContextItem, ...], char_budget: int | None = None) -> str:
        selected = self.select(items, char_budget=char_budget)
        if not selected:
            return self.policy.non_authoritative_banner()
        lines = [self.policy.non_authoritative_banner()]
        for item in selected:
            lines.append(f"- [{item.scope.value}/{item.sensitivity.value}] {item.content}")
        return "\n".join(lines)
