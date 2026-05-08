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
