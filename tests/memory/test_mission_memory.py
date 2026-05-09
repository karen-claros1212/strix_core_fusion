from saga_fusion.memory import MemoryStore, MissionMemory, MemorySensitivity


def test_mission_memory_redacts_user_intent_and_tracks_fields():
    store = MemoryStore()
    memory = MissionMemory(store)
    rec = memory.remember(
        mission_id="mission-1",
        user_intent="scan target with " + "STRIX_LLM" + "_API_KEY=" + "sk-" + "secret-value",
        policy_decision="approval_required",
        risk_level="R4",
        approval_status="pending",
        evidence_refs=("evidence:123",),
        report_refs=("report:abc",),
        outcome="planned",
        next_step="await approval",
    )
    assert rec.mission_id == "mission-1"
    assert rec.sensitivity == MemorySensitivity.SECRET_BLOCKED
    assert "sk-secret-value" not in rec.content
    assert rec.metadata["risk_level"] == "R4"
    assert store.list_by_mission("mission-1", include_secret_blocked=True)[0].record_id == rec.record_id
