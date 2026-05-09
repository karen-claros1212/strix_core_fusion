from saga_fusion.memory import MemoryRecord, MemoryScope, MemorySensitivity, MemoryStore


def test_store_add_get_search_list_delete_clear_session():
    store = MemoryStore()
    rec = store.add(MemoryRecord(content="project constraint MissionPolicy wins", scope=MemoryScope.PROJECT, mission_id="m1", session_id="s1"))
    assert store.get(rec.record_id) == rec
    assert store.search("MissionPolicy", scope=MemoryScope.PROJECT)[0].record_id == rec.record_id
    assert store.list_by_mission("m1")[0].record_id == rec.record_id
    assert store.delete(rec.record_id) is True
    assert store.get(rec.record_id) is None
    store.add(MemoryRecord(content="session note", session_id="s1"))
    assert store.clear_session("s1") == 1


def test_store_never_keeps_raw_secret_and_excludes_by_default():
    store = MemoryStore()
    rec = store.add(MemoryRecord(content="api_key=abcdef1234567890", sensitivity=MemorySensitivity.SENSITIVE))
    assert rec.sensitivity == MemorySensitivity.SECRET_BLOCKED
    assert "abcdef1234567890" not in rec.content
    assert store.search("api_key") == []
    assert store.get(rec.record_id, include_secret_blocked=False) is None
