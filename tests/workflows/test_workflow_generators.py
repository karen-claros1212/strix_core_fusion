from pathlib import Path

from saga_fusion.workflows import (
    generate_config_audit_plan,
    generate_dependency_audit_plan,
    generate_docker_audit_plan,
    generate_hardening_plan,
    generate_incident_response_plan,
    generate_log_review_plan,
    generate_repo_audit_plan,
    generate_secret_audit_plan,
)


def test_repo_dependency_secret_workflows_generate_plan_only(tmp_path):
    (tmp_path / "requirements.txt").write_text("requests==2.0\n")
    (tmp_path / "app.py").write_text("API_KEY='test-placeholder-token'\n")
    repo_plan = generate_repo_audit_plan(tmp_path)
    dep_plan = generate_dependency_audit_plan(tmp_path)
    secret_plan = generate_secret_audit_plan(tmp_path)
    assert repo_plan.execution_allowed is False
    assert dep_plan.evidence["external_calls"] is False
    assert "requirements.txt" in dep_plan.evidence["package_files"]
    assert secret_plan.evidence["findings"]
    assert "test-placeholder-token" not in str(secret_plan.to_dict())
    assert "[REDACTED]" in str(secret_plan.to_dict()) or "…[REDACTED]…" in str(secret_plan.to_dict())


def test_docker_fixture_detects_privileged_exposed_ports_and_redacts_env_secret(tmp_path):
    (tmp_path / "docker-compose.yml").write_text(
        """
services:
  app:
    image: test
    privileged: true
    ports:
      - "8080:80"
    volumes:
      - /host/path:/data
    environment:
      API_KEY: real-looking-secret-value
"""
    )
    plan = generate_docker_audit_plan(tmp_path)
    assert plan.execution_allowed is False
    assert plan.evidence["privileged_risks"]
    assert plan.evidence["exposed_ports"]
    assert plan.evidence["volume_mounts"]
    assert plan.evidence["env_secret_keys"][0]["value"] == "[REDACTED]"
    assert "real-looking-secret-value" not in str(plan.to_dict())


def test_config_fixture_detects_insecure_defaults(tmp_path):
    (tmp_path / ".env.example").write_text("SAFE_PLACEHOLDER=replace_me\n")
    (tmp_path / "settings.py").write_text("DEBUG = true\nSSL_VERIFY=false\nALLOWED_HOSTS='*'\n")
    plan = generate_config_audit_plan(tmp_path)
    rules = {finding["rule"] for finding in plan.evidence["insecure_defaults"]}
    assert {"debug_enabled", "tls_disabled", "wildcard_host"} <= rules
    assert plan.execution_allowed is False


def test_log_review_redacts_secrets_and_summarizes_errors(tmp_path):
    log = tmp_path / "app.log"
    log.write_text("ERROR failed token=supersecretvalue123\nINFO ok\n")
    plan = generate_log_review_plan(log)
    assert plan.evidence["anomaly_summary"]["error_count"] == 1
    rendered = str(plan.to_dict())
    assert "supersecretvalue123" not in rendered
    assert "[REDACTED]" in rendered
    assert plan.execution_allowed is False


def test_hardening_and_ir_are_plan_only_no_real_actions():
    hardening = generate_hardening_plan("local lab")
    ir = generate_incident_response_plan("suspicious login")
    assert hardening.execution_allowed is False
    assert ir.execution_allowed is False
    assert any("no_real_actions" in note for note in hardening.notes)
    assert any("no_real_containment" in note for note in ir.notes)
    assert hardening.evidence["execution_allowed"] is False
    assert ir.evidence["execution_allowed"] is False
