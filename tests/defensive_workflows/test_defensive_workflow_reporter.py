from saga_fusion.defensive_workflows import DefensiveWorkflowReporter, run_credential_theft_workflow, run_malware_triage_workflow
from saga_fusion.reporting import ReportBuilder


def test_reporter_builds_redacted_non_authoritative_reports():
    plan = run_credential_theft_workflow(summary="password=dummy_password_value token=dummy_token_value")
    report = DefensiveWorkflowReporter().build_report(plan)
    payload = report.to_dict()
    text = str(payload)
    assert report.execution_allowed is False
    assert report.non_authoritative is True
    assert report.redacted is True
    assert "dummy_password_value" not in text
    assert "dummy_token_value" not in text
    assert "[REDACTED]" in text
    assert "Execution allowed: False" in report.telegram_summary


def test_report_builder_generates_defensive_workflow_report():
    plan = run_malware_triage_workflow("stealer browser password")
    report = ReportBuilder().build_defensive_workflow_report(plan)
    assert report.workflow_id == plan.workflow_id
    assert report.execution_allowed is False
    assert report.non_authoritative is True
