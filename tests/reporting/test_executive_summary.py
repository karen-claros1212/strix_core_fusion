from saga_fusion.reporting import ExecutiveSummary, ReportBuilder


def test_executive_summary_mentions_r4_and_r5_status():
    report = ReportBuilder().build_mission_report(
        {'mission_id':'m1'},
        findings=[{'status':'blocked','risk_level':'R5'}],
        approvals=[{'approval_id':'a1','risk_level':'R4','status':'PENDING'}],
    )
    text = ExecutiveSummary().render(report)
    assert 'R4 approval required: yes' in text
    assert 'R5 blocked: yes' in text
    assert 'Recommended actions' in text
