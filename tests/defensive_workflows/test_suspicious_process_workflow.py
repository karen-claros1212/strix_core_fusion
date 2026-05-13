from saga_fusion.defensive_workflows import run_suspicious_process_workflow


def test_suspicious_process_plan_has_read_only_commands_and_no_kill():
    plan = run_suspicious_process_workflow(process_name="weird.exe", parent="winword.exe")
    assert plan.execution_allowed is False
    assert plan.evidence_required and plan.report_required
    assert plan.suggested_commands
    assert all(c.read_only and c.dry_run and c.execution_allowed is False for c in plan.suggested_commands)
    assert plan.evidence["kill_process"] is False
    assert "do not kill" in " ".join(plan.checklist).lower()
