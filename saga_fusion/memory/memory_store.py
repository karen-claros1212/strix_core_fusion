from __future__ import annotations

from dataclasses import replace
from typing import Iterable

from .memory_redactor import MemoryRedactor
from .memory_types import MemoryRecord, MemoryScope, MemorySensitivity, utc_now


class MemoryStore:
    """Process-local in-memory store. No external DB and no raw secret persistence."""

    def __init__(self, redactor: MemoryRedactor | None = None):
        self.redactor = redactor or MemoryRedactor()
        self._records: dict[str, MemoryRecord] = {}

    def add(self, record: MemoryRecord) -> MemoryRecord:
        redaction = self.redactor.redact_text(record.content)
        metadata = self.redactor.redact(record.metadata or {})
        if redaction.fingerprints:
            metadata = {**metadata, "secret_fingerprints": list(redaction.fingerprints), "redaction_reasons": list(redaction.reasons)}
        sensitivity = MemorySensitivity.SECRET_BLOCKED if redaction.secret_blocked else record.sensitivity
        stored = replace(
            record,
            content=redaction.text,
            sensitivity=sensitivity,
            metadata=metadata,
            authoritative=False,
            trusted=bool(record.trusted and record.scope != MemoryScope.USER_APPROVED),
            user_approved=bool(record.user_approved or record.scope == MemoryScope.USER_APPROVED),
            updated_at=utc_now(),
        )
        self._records[stored.record_id] = stored
        return stored

    def get(self, record_id: str, include_secret_blocked: bool = True) -> MemoryRecord | None:
        record = self._records.get(record_id)
        if record and record.sensitivity == MemorySensitivity.SECRET_BLOCKED and not include_secret_blocked:
            return None
        return record

    def search(
        self,
        query: str = "",
        *,
        scope: MemoryScope | None = None,
        sensitivity: MemorySensitivity | None = None,
        mission_id: str | None = None,
        include_secret_blocked: bool = False,
        limit: int | None = None,
    ) -> list[MemoryRecord]:
        terms = [t.lower() for t in str(query or "").split() if t.strip()]
        results: list[MemoryRecord] = []
        for record in self._records.values():
            if not include_secret_blocked and record.sensitivity == MemorySensitivity.SECRET_BLOCKED:
                continue
            if scope is not None and record.scope != scope:
                continue
            if sensitivity is not None and record.sensitivity != sensitivity:
                continue
            if mission_id is not None and record.mission_id != mission_id:
                continue
            haystack = f"{record.content} {record.metadata}".lower()
            if terms and not all(term in haystack for term in terms):
                continue
            results.append(record)
        results.sort(key=lambda r: r.created_at, reverse=True)
        return results[:limit] if limit is not None else results

    def list_by_mission(self, mission_id: str, include_secret_blocked: bool = False) -> list[MemoryRecord]:
        return self.search(mission_id=mission_id, include_secret_blocked=include_secret_blocked)

    def delete(self, record_id: str) -> bool:
        return self._records.pop(record_id, None) is not None

    def clear_session(self, session_id: str) -> int:
        doomed = [rid for rid, record in self._records.items() if record.session_id == session_id or record.scope == MemoryScope.SESSION]
        for rid in doomed:
            self._records.pop(rid, None)
        return len(doomed)

    def all(self, include_secret_blocked: bool = False) -> list[MemoryRecord]:
        return [r for r in self._records.values() if include_secret_blocked or r.sensitivity != MemorySensitivity.SECRET_BLOCKED]
