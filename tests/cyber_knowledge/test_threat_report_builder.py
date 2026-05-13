from saga_fusion.cyber_knowledge import IoC, IoCType, MalwareTaxonomy, ThreatReportBuilder


def test_threat_report_redacts_and_is_non_authoritative():
    classification = MalwareTaxonomy().classify("ransomware encrypt files ransom note")
    report = ThreatReportBuilder().build_report(
        "IR report token=abc123456789",
        classification,
        behaviors=["impact", "defense evasion"],
        iocs=[IoC("d41d8cd98f00b204e9800998ecf8427e", IoCType.HASH), "evil.example"],
        notes="api_key=secretvalue should not appear",
    )
    payload = report.to_dict()
    assert report.execution_allowed is False
    assert report.non_authoritative is True
    assert payload["classification"]["category"] == "ransomware"
    assert len(payload["mitre_mappings"]) == 2
    assert "secretvalue" not in str(payload)
    assert "abc123456789" not in str(payload)


def test_reporting_builder_generates_threat_report_wrapper():
    from saga_fusion.reporting.report_builder import ReportBuilder

    classification = MalwareTaxonomy().classify("backdoor covert access beacon")
    report = ReportBuilder().build_threat_report("Threat wrapper", classification, behaviors=["command and control"], iocs=["beacon.example"])
    assert report.execution_allowed is False
    assert report.metadata["schema_version"] == "10a"
    assert report.mitre_mappings[0]["tactic_id"] == "TA0011"
