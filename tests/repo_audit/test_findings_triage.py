import json
from saga_fusion.repo_audit.finding_triage import FindingsTriage


def test_findings_triage_deduplicates_fixture_and_report_groups(tmp_path):
    evidence = {
        "findings": [
            {"path": "reports/a.md", "line": 1, "category": "secret_scan", "severity": "HIGH", "title": "secret", "evidence": "API_KEY=[REDACTED]", "recommendation": "redact"},
            {"path": "reports/b.md", "line": 2, "category": "secret_scan", "severity": "HIGH", "title": "secret", "evidence": "API_KEY=[REDACTED]", "recommendation": "redact"},
            {"path": "tests/test_x.py", "line": 3, "category": "secret_scan", "severity": "HIGH", "title": "secret", "evidence": "api_key=[REDACTED]", "recommendation": "redact"},
            {"path": "saga_fusion/audit_logger.py", "line": 4, "category": "secret_scan", "severity": "HIGH", "title": "secret", "evidence": "api_key=[REDACTED]", "recommendation": "redact"},
        ]
    }
    path = tmp_path / "evidence.json"
    path.write_text(json.dumps(evidence))

    matrix = FindingsTriage(path).matrix()

    assert matrix["original_count"] == 4
    assert matrix["deduplicated_count"] == 3
    assert matrix["severity_counts"]["LOW"] == 1
    assert matrix["severity_counts"]["INFO"] == 2
    assert matrix["manual_review"] == 3


def test_findings_triage_env_example_is_autofix_safe_info(tmp_path):
    evidence = {"findings": [{"path": ".env.example", "line": 1, "category": "secret_scan", "severity": "HIGH", "title": "secret", "evidence": "TOKEN=[REDACTED]", "recommendation": "redact"}]}
    path = tmp_path / "evidence.json"
    path.write_text(json.dumps(evidence))

    finding = FindingsTriage(path).triage()[0]

    assert finding.severity == "INFO"
    assert finding.priority == "P3"
    assert finding.auto_fix_safe is True
