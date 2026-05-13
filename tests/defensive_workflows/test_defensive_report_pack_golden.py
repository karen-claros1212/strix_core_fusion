from __future__ import annotations

import json

import pytest

from saga_fusion.defensive_workflows import DefensiveWorkflowRegistry, DefensiveWorkflowReporter
from saga_fusion.telegram.defensive_command_router import DefensiveCommandRouter
from saga_fusion.telegram.lab_mode import assert_lab_mode


def _walk(value):
    if isinstance(value, dict):
        yield value
        for item in value.values():
            yield from _walk(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _walk(item)


def _assert_no_raw_artifact_slots(payload):
    forbidden_keys = {"raw", "raw_body", "body", "artifact_body", "attachment_body", "sample_body", "file_contents", "attachment_contents", "sample_contents"}
    for item in _walk(payload):
        assert forbidden_keys.isdisjoint(set(item.keys()))


def _assert_defensive_invariants(payload):
    assert payload["execution_allowed"] is False
    assert payload["executed"] is False
    assert payload["evidence_required"] is True
    assert payload["report_required"] is True
    assert payload["non_authoritative"] is True


@pytest.mark.parametrize(
    ("workflow_id", "kwargs"),
    [
        ("malware_triage", {"observations": "ransomware-like behavior", "reported_iocs": ["sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"]}),
        ("ransomware_response", {"incident_summary": "ransom note metadata observed", "affected_scope": "lab-host-alias"}),
        ("phishing_attachment", {"subject": "Invoice lure", "attachment_name": "invoice_metadata_only.docm", "sender": "sender@example.invalid"}),
        ("webshell_investigation", {"web_root": "/var/www/example", "suspicious_path": "uploads/suspect.php"}),
        ("credential_theft", {"summary": "token=dummy_token_value password=dummy_password_value", "affected_identity": "user-alias"}),
        ("suspicious_process", {"process_name": "suspicious.exe", "command_line": "", "parent": "parent.exe", "user": "user-alias"}),
    ],
)
def test_defensive_workflow_outputs_are_pack_ready_golden(workflow_id, kwargs):
    plan = DefensiveWorkflowRegistry().run(workflow_id, **kwargs)
    payload = plan.to_dict()

    assert payload["workflow_id"].startswith(workflow_id.replace("_", "-").split("-")[0])
    assert payload["title"]
    assert payload["summary"]
    assert isinstance(payload["classification"], dict) and payload["classification"]
    assert isinstance(payload["mitre_mappings"], list)
    assert isinstance(payload["indicators"], list)
    assert isinstance(payload["evidence"], dict) and payload["evidence"]
    assert isinstance(payload["checklist"], list) and payload["checklist"]
    assert isinstance(payload["recommendations"], list) and payload["recommendations"]
    assert payload["metadata"].get("toolrouter_executes") is False
    _assert_defensive_invariants(payload)
    _assert_no_raw_artifact_slots(payload)

    serialized = json.dumps(payload, sort_keys=True)
    assert "dummy_token_value" not in serialized
    assert "dummy_password_value" not in serialized
    assert "execution_allowed\": true" not in serialized.lower()


def test_existing_defensive_reporter_is_future_pack_building_block_golden():
    plan = DefensiveWorkflowRegistry().run(
        "credential_theft",
        summary="token=dummy_token_value password=dummy_password_value",
        affected_identity="identity-alias",
    )
    report = DefensiveWorkflowReporter().build_report(plan)
    payload = report.to_dict()
    serialized = json.dumps(payload, sort_keys=True)

    assert payload["workflow_id"] == plan.workflow_id
    assert payload["redacted"] is True
    assert payload["non_authoritative"] is True
    assert payload["execution_allowed"] is False
    assert payload["metadata"]["active_redaction"] is True
    assert payload["metadata"]["schema_version"] == "defensive_workflow_report_v1"
    assert "dummy_token_value" not in serialized
    assert "dummy_password_value" not in serialized
    assert "[REDACTED]" in serialized
    _assert_no_raw_artifact_slots(payload)


@pytest.mark.parametrize(
    ("command", "workflow_category"),
    [
        ("/malware_triage token=dummy_token_value password=dummy_password_value", "malware_triage"),
        ("/ransomware_response", "ransomware_response"),
        ("/phishing_review", "phishing_attachment"),
        ("/webshell_investigation", "webshell_investigation"),
        ("/credential_theft_review token=dummy_token_value password=dummy_password_value", "credential_theft"),
        ("/suspicious_process_review", "suspicious_process"),
    ],
)
def test_telegram_lab_mode_workflow_summaries_are_safe_pack_inputs(command, workflow_category):
    result = DefensiveCommandRouter().route(command)
    serialized = json.dumps(result, sort_keys=True)

    assert result["status"] == "workflow_plan"
    assert result["workflow_category"] == workflow_category
    assert result["artifact_ref"].startswith("reports/defensive_telegram/defensive-report-")
    assert result["report_id"].startswith("defensive-report-")
    assert "telegram_summary" in result and len(result["telegram_summary"]) <= 1800
    assert assert_lab_mode(result) is True
    _assert_defensive_invariants(result)
    _assert_no_raw_artifact_slots(result)
    assert "dummy_token_value" not in serialized
    assert "dummy_password_value" not in serialized
    assert result["raw_secret_display"] is False
    assert result["real_attachment_processing"] is False


def test_defense_status_is_safe_report_pack_control_surface_golden():
    result = DefensiveCommandRouter().route("/defense_status")

    assert result["status"] == "ok"
    assert result["workflow_category"] == "defense_status"
    assert sorted(result["available_workflows"]) == sorted(
        [definition.workflow_id for definition in DefensiveWorkflowRegistry().list_workflows()]
    )
    assert assert_lab_mode(result) is True
    _assert_defensive_invariants(result)
    _assert_no_raw_artifact_slots(result)
    assert "modo laboratorio activo" in result["telegram_summary"]
