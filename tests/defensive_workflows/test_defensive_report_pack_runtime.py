from __future__ import annotations

import json
import re

import pytest

from saga_fusion.defensive_workflows import DefensiveWorkflowRegistry, DefensiveWorkflowReporter


SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
FORBIDDEN_KEYS = {
    "raw",
    "raw_body",
    "body",
    "artifact_body",
    "attachment_body",
    "sample_body",
    "file_contents",
    "attachment_contents",
    "sample_contents",
    "content",
    "text",
}


def _walk(value):
    if isinstance(value, dict):
        yield value
        for item in value.values():
            yield from _walk(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _walk(item)


def _assert_no_raw_artifact_slots(payload):
    for item in _walk(payload):
        assert FORBIDDEN_KEYS.isdisjoint(set(item.keys()))


def _assert_pack_invariants(payload):
    assert payload["execution_allowed"] is False
    assert payload["executed"] is False
    assert payload["non_authoritative"] is True
    assert payload["evidence_required"] is True
    assert payload["report_required"] is True
    assert payload["metadata"]["schema_version"] == "defensive_report_pack_v1"
    assert payload["metadata"]["thin_aggregation_layer"] is True
    assert payload["metadata"]["real_telegram_used"] is False
    assert payload["metadata"]["real_llm_used"] is False
    assert payload["metadata"]["real_tool_execution"] is False
    assert payload["metadata"]["raw_artifact_bodies_embedded"] is False


@pytest.mark.parametrize(
    ("workflow_id", "kwargs", "category"),
    [
        ("malware_triage", {"observations": "token=dummy_token_value ransomware-like metadata", "reported_iocs": ["sha256:" + "a" * 64]}, "malware_triage"),
        ("ransomware_response", {"incident_summary": "ransom note metadata only", "affected_scope": "lab-host-alias"}, "ransomware_response"),
        ("phishing_attachment", {"subject": "Invoice lure", "attachment_name": "invoice.docm", "sender": "sender@example.invalid"}, "phishing_attachment"),
        ("webshell_investigation", {"web_root": "/var/www/example", "suspicious_path": "uploads/suspect.php"}, "webshell_investigation"),
        ("credential_theft", {"summary": "token=dummy_token_value password=dummy_password_value", "affected_identity": "identity-alias"}, "credential_theft"),
        ("suspicious_process", {"process_name": "suspicious.exe", "command_line": "password=dummy_password_value", "parent": "parent.exe", "user": "user-alias"}, "suspicious_process"),
        ("defense_status", {"available_workflows": ["malware_triage", "defense_status"]}, "defense_status"),
    ],
)
def test_defensive_report_pack_runtime_fields_and_safety(workflow_id, kwargs, category):
    plan = DefensiveWorkflowRegistry().run(workflow_id, **kwargs)
    pack = DefensiveWorkflowReporter().build_report_pack(plan).to_dict()
    serialized = json.dumps(pack, sort_keys=True)

    required = {
        "executive_summary",
        "technical_findings",
        "risk_classification",
        "recommended_actions",
        "containment_steps",
        "recovery_steps",
        "lessons_learned",
        "evidence_refs",
        "report_refs",
        "manifest_refs",
        "non_authoritative",
        "execution_allowed",
        "executed",
        "evidence_required",
        "report_required",
    }
    assert required.issubset(pack.keys())
    assert pack["workflow_category"] == category
    assert pack["pack_id"].startswith("defensive-pack-")
    assert pack["report_id"].startswith("defensive-report-")
    assert pack["technical_findings"]["evidence_reference_only"] is True
    assert pack["technical_findings"]["raw_artifact_bodies_embedded"] is False
    assert pack["evidence_refs"] and pack["report_refs"] and pack["manifest_refs"]
    _assert_pack_invariants(pack)
    _assert_no_raw_artifact_slots(pack)
    assert "dummy_token_value" not in serialized
    assert "dummy_password_value" not in serialized
    assert "execution_allowed\": true" not in serialized.lower()


def test_defensive_report_pack_uses_reference_hashes_not_bodies():
    plan = DefensiveWorkflowRegistry().run(
        "credential_theft",
        summary="Authorization: Bearer dummy.secret.value token=dummy_token_value password=dummy_password_value",
        affected_identity="identity-alias",
    )
    pack = DefensiveWorkflowReporter().build_report_pack(plan).to_dict()
    serialized = json.dumps(pack, sort_keys=True)

    evidence_ref = pack["evidence_refs"][0]
    report_ref = pack["report_refs"][0]
    assert evidence_ref["ref"].startswith("defensive-workflow://credential_theft/")
    assert report_ref["ref"].startswith("defensive-report://defensive-report-")
    assert SHA256_RE.match(evidence_ref["sha256"])
    assert SHA256_RE.match(report_ref["sha256"])
    assert evidence_ref["redaction_status"] == "redacted"
    assert evidence_ref["secret_scan_status"] == "clean"
    assert report_ref["evidence_refs"] == [evidence_ref["artifact_id"]]
    assert "dummy.secret.value" not in serialized
    assert "dummy_token_value" not in serialized
    assert "dummy_password_value" not in serialized
    _assert_no_raw_artifact_slots(pack)


def test_registry_resolves_defensive_workflows_deterministically_and_blocks_unknown():
    registry = DefensiveWorkflowRegistry()
    expected = [
        "malware_triage",
        "ransomware_response",
        "phishing_attachment",
        "webshell_investigation",
        "credential_theft",
        "suspicious_process",
        "defense_status",
    ]

    assert [definition.workflow_id for definition in registry.list_workflows()] == expected
    for workflow_id in expected:
        definition = registry.resolve(workflow_id)
        assert definition is not None
        assert definition.workflow_id == workflow_id
        assert definition.execution_allowed is False
        assert definition.evidence_required is True
        assert definition.report_required is True
        assert definition.non_authoritative is True

    assert registry.resolve("unknown") is None
    blocked = registry.blocked_unknown("unknown")
    assert blocked["blocked"] is True
    assert blocked["execution_allowed"] is False
    assert blocked["reason"] == "unknown_defensive_workflow"


def test_defensive_report_pack_rejects_executed_or_authoritative_inputs():
    reporter = DefensiveWorkflowReporter()
    unsafe = DefensiveWorkflowRegistry().run("malware_triage", observations="metadata only").to_dict()

    with pytest.raises(ValueError):
        reporter.build_report_pack({**unsafe, "execution_allowed": True})
    with pytest.raises(ValueError):
        reporter.build_report_pack({**unsafe, "executed": True})
    with pytest.raises(ValueError):
        reporter.build_report_pack({**unsafe, "non_authoritative": False})
