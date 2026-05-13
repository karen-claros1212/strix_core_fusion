from saga_fusion.defensive_workflows import run_ransomware_response_workflow


def test_ransomware_response_plan_no_deletion_or_crypto_actions():
    plan = run_ransomware_response_workflow("ransom notes and extension changes", affected_scope="lab-hosts")
    assert plan.execution_allowed is False
    assert plan.evidence_required and plan.report_required
    assert plan.classification["category"] == "ransomware"
    assert plan.evidence["isolation_recommended"] is True
    assert plan.evidence["isolation_executed"] is False
    assert plan.evidence["snapshot_backup_review_plan"] is True
    assert plan.evidence["file_deletion"] is False
    assert plan.evidence["encryption_decryption"] is False
