from __future__ import annotations

import json
import re
from dataclasses import dataclass

import pytest

from saga_fusion.defensive_workflows import DefensiveWorkflowRegistry, DefensiveWorkflowReporter
from saga_fusion.defensive_workflows.defensive_workflow_registry import DefensiveWorkflowDefinition
from saga_fusion.defensive_workflows.defensive_workflow_types import DefensiveWorkflowPlan
from saga_fusion.reporting import EvidenceReporter
from saga_fusion.telegram.defensive_command_router import DefensiveCommandRouter
from saga_fusion.telegram.lab_mode import assert_lab_mode
from saga_fusion.telegram.mission_policy import MissionPolicy
from saga_fusion.telegram.telegram_types import MissionRequest, RiskLevel
from saga_fusion.tool_routing import ToolRouter


SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
SECRET_VALUES = ("dummy_token_value", "dummy_password_value", "dummy.secret.value", "super-secret-body")
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


def _assert_no_raw_slots(value):
    for item in _walk(value):
        assert FORBIDDEN_KEYS.isdisjoint(item.keys())


def _assert_no_secret_values(value):
    serialized = json.dumps(value, sort_keys=True)
    for secret in SECRET_VALUES:
        assert secret not in serialized
    assert "Authorization: Bearer dummy.secret.value" not in serialized


def _fixed_plan_payload() -> dict:
    return {
        "workflow_id": "credential-theft-fixed",
        "title": "Credential Theft Review",
        "summary": "Authorization: Bearer dummy.secret.value token=dummy_token_value password=dummy_password_value",
        "classification": {"category": "stealer", "confidence": 0.91, "summary": "metadata-only"},
        "mitre_mappings": [{"technique_id": "T1555", "name": "Credentials from Password Stores"}],
        "indicators": [{"ioc_type": "domain", "value": "example.invalid"}],
        "evidence": {
            "raw_body": "super-secret-body",
            "attachment_contents": "token=dummy_token_value",
            "safe_key": "metadata-only",
        },
        "checklist": ["Review identity provider alerts"],
        "recommendations": ["Rotate exposed sessions through approved IAM owners"],
        "report_required": True,
        "evidence_required": True,
        "non_authoritative": True,
        "execution_allowed": False,
        "executed": False,
        "metadata": {"toolrouter_executes": False},
    }


def test_report_pack_does_not_embed_raw_artifact_bodies_or_secrets():
    pack = DefensiveWorkflowReporter().build_report_pack(_fixed_plan_payload()).to_dict()

    _assert_no_raw_slots(pack)
    _assert_no_secret_values(pack)
    assert pack["technical_findings"]["evidence_reference_only"] is True
    assert pack["metadata"]["raw_artifact_bodies_embedded"] is False
    assert pack["execution_allowed"] is False
    assert pack["executed"] is False


def test_reporter_technical_report_reuses_evidence_metadata_not_raw_evidence():
    report = DefensiveWorkflowReporter().build_report(_fixed_plan_payload()).to_dict()
    serialized = json.dumps(report, sort_keys=True)

    assert "evidence_keys" in serialized
    assert "safe_key" in serialized
    assert "super-secret-body" not in serialized
    assert "attachment_contents" not in serialized
    assert "raw_body" not in serialized
    assert report["execution_allowed"] is False
    _assert_no_secret_values(report)


def test_report_pack_sha256_refs_are_stable_valid_and_reference_only():
    reporter = DefensiveWorkflowReporter()
    first = reporter.build_report_pack(_fixed_plan_payload()).to_dict()
    second = reporter.build_report_pack(_fixed_plan_payload()).to_dict()

    first_refs = (first["evidence_refs"], first["report_refs"], first["manifest_refs"])
    second_refs = (second["evidence_refs"], second["report_refs"], second["manifest_refs"])
    assert first_refs == second_refs
    assert first["pack_id"] == second["pack_id"]
    assert first["report_id"] == second["report_id"]
    assert SHA256_RE.match(first["evidence_refs"][0]["sha256"])
    assert SHA256_RE.match(first["report_refs"][0]["sha256"])
    assert first["evidence_refs"][0]["ref"].startswith("defensive-workflow://")
    assert first["report_refs"][0]["ref"].startswith("defensive-report://")
    assert "body" not in first["evidence_refs"][0]


def test_report_pack_output_is_deterministic_except_existing_runtime_workflow_ids():
    reporter = DefensiveWorkflowReporter()
    first = reporter.build_report_pack(_fixed_plan_payload()).to_dict()
    second = reporter.build_report_pack(_fixed_plan_payload()).to_dict()

    assert first == second


def test_evidence_reporter_manifest_ref_redacts_and_hashes_without_body(tmp_path):
    evidence = tmp_path / "evidence.json"
    evidence.write_text('{"records": [{"token": "dummy_token_value", "body": "super-secret-body"}]}')

    loaded = EvidenceReporter().load(evidence)
    ref = EvidenceReporter().build_manifest_ref(
        evidence,
        source_phase="10D-4",
        classification="internal",
        risk="R1",
        metadata={"purpose": "defensive_report_pack_integration"},
    )

    assert loaded["records"][0]["token"] == "[REDACTED]"
    assert "super-secret-body" in json.dumps(loaded, sort_keys=True)
    ref_payload = ref.to_dict()
    assert SHA256_RE.match(ref_payload["sha256"])
    assert "super-secret-body" not in json.dumps(ref_payload, sort_keys=True)
    assert "dummy_token_value" not in json.dumps(ref_payload, sort_keys=True)
    assert "body" not in ref_payload["metadata"]
    assert ref_payload["execution_allowed"] is False


def test_registry_blocks_unknown_empty_and_invalid_workflows():
    registry = DefensiveWorkflowRegistry()
    assert registry.resolve("unknown") is None
    assert registry.resolve("  ") is None
    blocked = registry.blocked_unknown("unknown")
    assert blocked == {
        "workflow_id": "unknown",
        "blocked": True,
        "reason": "unknown_defensive_workflow",
        "execution_allowed": False,
    }

    def valid_runner(**_kwargs):
        return DefensiveWorkflowPlan(
            workflow_id="invalid-test-instance",
            title="Invalid Test",
            summary="metadata only",
            classification={"category": "unknown", "confidence": 0.1},
            evidence={"metadata": True},
            checklist=["review"],
            recommendations=["do not execute"],
        )

    with pytest.raises(ValueError):
        registry.register(DefensiveWorkflowDefinition("", "Empty", valid_runner))
    with pytest.raises(ValueError):
        registry.register(DefensiveWorkflowDefinition("invalid", "Invalid", valid_runner, non_authoritative=False))
    with pytest.raises(ValueError):
        registry.register(DefensiveWorkflowDefinition("invalid", "Invalid", valid_runner, execution_allowed=True))


def test_defensive_lab_router_remains_non_executing_for_pack_inputs():
    result = DefensiveCommandRouter().route(
        "/credential_theft_review token=dummy_token_value password=dummy_password_value"
    )
    serialized = json.dumps(result, sort_keys=True)

    assert result["status"] == "workflow_plan"
    assert result["workflow_category"] == "credential_theft"
    assert assert_lab_mode(result) is True
    assert result["execution_allowed"] is False
    assert result["executed"] is False
    assert result["plan"]["execution_allowed"] is False
    assert result["plan"]["executed"] is False
    assert "dummy_token_value" not in serialized
    assert "dummy_password_value" not in serialized
    assert result["real_telegram_used"] is False


def test_advanced_authorized_paths_not_globally_capped_by_report_packs():
    policy = MissionPolicy()
    assert policy.classify_risk(MissionRequest(action_type="create", target="vps")) == RiskLevel.R4
    assert policy.requires_approval(RiskLevel.R4) is True
    assert policy.is_blocked(RiskLevel.R4) is False

    router = ToolRouter()
    safe_decision = router.route_tool_request({"tool_name": "status", "action_type": "status"})
    safe_plan = router.build_execution_plan(safe_decision, {"action_type": "status"})
    assert safe_decision.allowed is True
    assert safe_decision.blocked is False
    assert safe_plan.execution_allowed is True

    advanced_decision = router.route_tool_request({"tool_name": "cloudops_plan", "action_type": "create", "target": "vps"})
    advanced_plan = router.build_execution_plan(advanced_decision, {"action_type": "create", "target": "vps"})
    assert advanced_decision.blocked is False
    assert advanced_decision.approval_required is True
    assert advanced_plan.execution_allowed is False
