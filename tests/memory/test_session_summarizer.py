from saga_fusion.memory import SessionSummarizer, MemorySensitivity


def test_session_summarizer_includes_decisions_risks_approvals_evidence_no_secrets():
    summary = SessionSummarizer().summarize([
        {"event": "policy_decision", "decision": "approval_required", "risk_level": "R4", "evidence_ref": "mission:1"},
        {"event": "approval", "approval_id": "ap-1", "status": "PENDING", "next_step": "await user"},
        {"event": "note", "decision": "token=abcdef1234567890"},
    ])
    assert "approval_required" in summary.text
    assert "R4" in summary.text
    assert "mission:1" in summary.text
    assert "abcdef1234567890" not in summary.text
    assert summary.sensitivity == MemorySensitivity.SECRET_BLOCKED
