from saga_fusion.reporting import ReportBuilder, ReportAudience


def test_report_builder_generates_structured_report_with_data():
    report = ReportBuilder().build_mission_report(
        {'mission_id':'m1','status':'dry_run'},
        findings=[{'title':'finding','severity':'HIGH','recommendation':'fix'}],
        approvals=[{'approval_id':'a1','risk_level':'R4','status':'PENDING'}],
        evidence=[{'event_type':'sandbox'}],
        audience='technical',
    )
    assert report.audience == ReportAudience.TECHNICAL
    names = {s.name for s in report.sections}
    assert {'scope','summary','risk_overview','findings','approvals','evidence','recommendations','residual_risk'} <= names


def test_report_builder_handles_missing_fields():
    report = ReportBuilder().build_mission_report({}, audience='technical')
    assert report.title
    assert report.sections
