from saga_fusion.reporting import ReportBuilder, TelegramReportFormatter


def test_telegram_formatter_truncates_preserves_artifact_and_redacts():
    report = ReportBuilder().build_mission_report(
        {'mission_id':'m1'},
        findings=[{'title':'x'*5000, 'evidence':'Authorization: Bearer SECRET'}],
        approvals=[{'approval_id':'a1','status':'PENDING'}],
        audience='telegram_summary',
    )
    text = TelegramReportFormatter(max_length=220).format(report, artifact_ref='reports/a.md')
    assert len(text) <= 260
    assert 'reports/a.md' in text
    assert 'SECRET' not in text
