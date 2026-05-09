from saga_fusion.memory import MemoryRecord, MemoryRetriever, MemoryScope, MemorySensitivity, MemoryStore


def test_memory_retriever_relevance_scope_sensitivity_limit():
    store = MemoryStore()
    store.add(MemoryRecord("alpha mission evidence", scope=MemoryScope.MISSION, mission_id="m1", sensitivity=MemorySensitivity.INTERNAL))
    store.add(MemoryRecord("beta project constraint", scope=MemoryScope.PROJECT, sensitivity=MemorySensitivity.INTERNAL))
    store.add(MemoryRecord("alpha public note", scope=MemoryScope.SESSION, sensitivity=MemorySensitivity.PUBLIC))
    store.add(MemoryRecord("alpha token=abcdef1234567890", scope=MemoryScope.MISSION, mission_id="m1"))
    result = MemoryRetriever(store).retrieve("alpha", scope=MemoryScope.MISSION, sensitivity=MemorySensitivity.INTERNAL, limit=1)
    assert result.count == 1
    assert result.records[0].mission_id == "m1"
    assert result.records[0].sensitivity == MemorySensitivity.INTERNAL
    assert "non-authoritative" in result.reasons[0]
    assert all(r.sensitivity != MemorySensitivity.SECRET_BLOCKED for r in result.records)
