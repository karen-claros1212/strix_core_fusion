from saga_fusion.repo_audit import RepoAuditor, RepoAuditReportEngine


def test_repo_auditor_detects_secret_and_docker_risk(tmp_path):
    (tmp_path / "app.py").write_text("import os\nTOKEN=\"x\"\n")
    (tmp_path / ".env.example").write_text("SAFE_PLACEHOLDER=\n")
    (tmp_path / "docker-compose.yml").write_text("services:\n  app:\n    privileged: true\n")
    (tmp_path / "config.ini").write_text("debug=true\n")
    (tmp_path / "secret.txt").write_text("api_key=supersecret\n")

    result = RepoAuditor(tmp_path).audit()

    assert result.file_count == 5
    assert any(f.category == "secret_scan" and f.severity == "HIGH" for f in result.findings)
    assert any(f.category == "docker_audit" for f in result.findings)
    assert any(f.category == "config_audit" for f in result.findings)
    assert all("supersecret" not in f.evidence for f in result.findings)


def test_repo_audit_report_renders_dry_run_verdict(tmp_path):
    (tmp_path / "app.py").write_text("import json\n")
    result = RepoAuditor(tmp_path).audit()
    report = RepoAuditReportEngine().render_markdown(result, evidence_path="evidence.json")

    assert "dry-run" in report.lower()
    assert "APTO PARA CONTINUAR 6C LAB: SI" in report
    assert "json" in report


def test_repo_auditor_allows_safe_env_example_placeholders(tmp_path):
    (tmp_path / ".env.example").write_text("STRIX_LLM_API_KEY=local\nTELEGRAM_BOT_TOKEN=\n")

    result = RepoAuditor(tmp_path).audit()

    assert not result.findings


def test_repo_auditor_skips_config_audit_inside_tests(tmp_path):
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_config_fixture.py").write_text("debug=true\nallowed_networks=['10.0.0.0/8']\n")

    result = RepoAuditor(tmp_path).audit()

    assert not any(f.category == "config_audit" for f in result.findings)


def test_repo_auditor_classifies_redaction_regex_self_reference(tmp_path):
    pkg = tmp_path / "saga_fusion"
    pkg.mkdir()
    (pkg / "audit_logger.py").write_text(
        "def redact_secrets(value):\n"
        "    patterns = [\n"
        "        (r'(?i)api[_-]?key\\s*[=:]\\s*([a-zA-Z0-9_-]+)', r'api_key=[REDACTED]'),\n"
        "    ]\n"
    )

    result = RepoAuditor(tmp_path).audit()

    assert any(f.category == "scanner_self_reference" and f.severity == "INFO" for f in result.findings)
    assert not any(f.category == "secret_scan" for f in result.findings)


def test_repo_auditor_still_detects_real_secret_in_runtime_code(tmp_path):
    pkg = tmp_path / "saga_fusion"
    pkg.mkdir()
    (pkg / "runtime_config.py").write_text("API_KEY=real_runtime_secret\n")

    result = RepoAuditor(tmp_path).audit()

    assert any(f.category == "secret_scan" and f.severity == "HIGH" for f in result.findings)


def test_repo_auditor_classifies_synthetic_test_fixture(tmp_path):
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_redaction.py").write_text("cfg = 'api_key=secret-key'\n")

    result = RepoAuditor(tmp_path).audit()

    assert any(f.category == "synthetic_fixture" and f.severity == "INFO" for f in result.findings)
    assert not any(f.category == "secret_scan" for f in result.findings)


def test_repo_auditor_classifies_historical_evidence_placeholder(tmp_path):
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    (reports_dir / "PHASE_REPORT.md").write_text("STRIX_LLM_API_KEY=local was used as a placeholder\n")

    result = RepoAuditor(tmp_path).audit()

    assert any(f.category == "historical_evidence" and f.severity == "INFO" for f in result.findings)
    assert not any(f.category == "secret_scan" for f in result.findings)
