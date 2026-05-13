from saga_fusion.defensive_workflows import run_phishing_attachment_workflow


def test_phishing_attachment_static_analysis_only_no_execution():
    plan = run_phishing_attachment_workflow(subject="invoice", attachment_name="invoice.docm", sender="sender.example")
    assert plan.execution_allowed is False
    assert plan.evidence_required and plan.report_required
    assert plan.evidence["attachment_execution"] is False
    assert plan.evidence["detonation"] is False
    assert plan.yara_rules and plan.sigma_rules
    assert "do not open" in " ".join(plan.checklist).lower()
