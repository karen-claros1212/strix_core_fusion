from __future__ import annotations

from .memory_store import MemoryStore
from .memory_types import MemoryRecord, MemoryRetrievalResult, MemoryScope, MemorySensitivity


class MemoryRetriever:
    def __init__(self, store: MemoryStore):
        self.store = store

    def retrieve(
        self,
        query: str = "",
        *,
        scope: MemoryScope | None = None,
        sensitivity: MemorySensitivity | None = None,
        mission_id: str | None = None,
        limit: int = 5,
    ) -> MemoryRetrievalResult:
        candidates = self.store.search(
            "",
            scope=scope,
            sensitivity=sensitivity,
            mission_id=mission_id,
            include_secret_blocked=False,
        )
        terms = [t.lower() for t in str(query or "").split() if t.strip()]

        def score(record: MemoryRecord) -> tuple[int, str]:
            haystack = f"{record.content} {record.metadata}".lower()
            relevance = sum(3 for term in terms if term in haystack)
            if terms and all(term in haystack for term in terms):
                relevance += 5
            scope_bonus = {MemoryScope.PROJECT: 3, MemoryScope.MISSION: 2, MemoryScope.USER_APPROVED: 1, MemoryScope.SESSION: 0}.get(record.scope, 0)
            return (relevance + scope_bonus, record.created_at)

        ranked = sorted(candidates, key=score, reverse=True)
        if terms:
            ranked = [r for r in ranked if score(r)[0] > {MemoryScope.PROJECT:3, MemoryScope.MISSION:2, MemoryScope.USER_APPROVED:1, MemoryScope.SESSION:0}.get(r.scope,0)]
        selected = tuple(ranked[: max(0, limit)])
        reasons = tuple(f"matched query '{query}' within {r.scope.value}; non-authoritative" for r in selected)
        return MemoryRetrievalResult(query=str(query or ""), records=selected, reasons=reasons, limit=limit)
