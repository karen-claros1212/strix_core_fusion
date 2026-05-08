from saga_fusion.reporting import ReportBuilder, TechnicalReport


def test_technical_report_includes_evidence_remediation_and_redacts_secrets():
    report = ReportBuilder().build_mission_report(
        {'mission_id':'m1'},
        findings=[{'file':'app.py','severity':'HIGH','confidence':'HIGH','evidence':'STRIX_LLM_API_KEY=secret','recommendation':'rotate key'}],
        evidence=[{'ref':'ev1'}],
    )
    text = TechnicalReport().render(report)
    assert 'ev1' in text
    assert 'rotate key' in text
    assert 'secret' not in text
    assert 'STRIX_LLM_API_KEY=[REDACTED]' in text
