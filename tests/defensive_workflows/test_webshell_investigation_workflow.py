from saga_fusion.defensive_workflows import run_webshell_investigation_workflow


def test_webshell_investigation_has_defensive_rules_no_generation():
    plan = run_webshell_investigation_workflow(web_root="/var/www", suspicious_path="uploads/a.php")
    assert plan.execution_allowed is False
    assert plan.evidence_required and plan.report_required
    assert plan.yara_rules and plan.sigma_rules
    assert plan.evidence["webshell_generation"] is False
    assert plan.evidence["endpoint_invocation"] is False
    assert "do not generate" in " ".join(plan.checklist).lower()
