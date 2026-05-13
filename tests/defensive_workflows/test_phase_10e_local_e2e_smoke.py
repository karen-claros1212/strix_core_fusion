from __future__ import annotations

import json
import re

from saga_fusion.defensive_workflows import DefensiveWorkflowReporter
from saga_fusion.telegram.defensive_command_router import DefensiveCommandRouter
from saga_fusion.telegram.defensive_commands import map_natural_language
from saga_fusion.telegram.lab_mode import assert_lab_mode

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


def _assert_non_executing_invariants(payload):
    assert payload["execution_allowed"] is False
    assert payload["executed"] is False
    assert payload["non_authoritative"] is True
    assert payload["evidence_required"] is True
    assert payload["report_required"] is True


def test_phase_10e_local_phishing_attachment_e2e_smoke_no_real_services():
    """Local-only E2E smoke: simulated Telegram text -> router -> workflow -> report pack -> final output."""

    simulated_input = "revisa un adjunto sospechoso en modo seguro"
    router = DefensiveCommandRouter()

    # Classification/router: deterministic local natural-language mapping only.
    request = map_natural_language(simulated_input)
    assert request is not None
    assert request.source == "natural_language"
    assert request.workflow_id == "phishing_attachment"
    assert router.can_handle(simulated_input) is True

    # Workflow/final Telegram-lab output: no real Telegram, no attachment processing/execution.
    routed = router.route(simulated_input, chat_id="lab-chat", user_id="lab-user")
    assert routed["status"] == "workflow_plan"
    assert routed["workflow_category"] == "phishing_attachment"
    assert routed["plan"]["workflow_id"].startswith("phishing-attachment-")
    assert routed["artifact_ref"].startswith("reports/defensive_telegram/defensive-report-")
    assert routed["real_telegram_used"] is False
    assert routed["real_tool_execution"] is False
    assert routed["attachment_processed"] is False
    assert routed["attachment_executed"] is False
    assert routed["raw_secret_display"] is False
    assert routed["real_attachment_processing"] is False
    assert assert_lab_mode(routed) is True
    _assert_non_executing_invariants(routed)

    # Report pack: evidence/report refs and manifests are reference-only, redacted, and stable-hashed.
    pack = DefensiveWorkflowReporter().build_report_pack(routed["plan"]).to_dict()
    _assert_non_executing_invariants(pack)
    assert pack["workflow_category"] == "phishing_attachment"
    assert pack["workflow_id"].startswith("phishing-attachment-")
    assert pack["metadata"]["real_telegram_used"] is False
    assert pack["metadata"]["real_llm_used"] is False
    assert pack["metadata"]["real_tool_execution"] is False
    assert pack["metadata"]["raw_artifact_bodies_embedded"] is False
    assert pack["technical_findings"]["evidence_reference_only"] is True
    assert pack["technical_findings"]["raw_artifact_bodies_embedded"] is False
    assert pack["evidence_refs"] and pack["report_refs"] and pack["manifest_refs"]
    assert SHA256_RE.match(pack["evidence_refs"][0]["sha256"])
    assert SHA256_RE.match(pack["report_refs"][0]["sha256"])
    assert pack["evidence_refs"][0]["redaction_status"] == "redacted"
    assert pack["evidence_refs"][0]["secret_scan_status"] == "clean"

    final_output = {
        "telegram_summary": routed["telegram_summary"],
        "report_id": pack["report_id"],
        "pack_id": pack["pack_id"],
        "evidence_refs": pack["evidence_refs"],
        "report_refs": pack["report_refs"],
        "manifest_refs": pack["manifest_refs"],
        "execution_allowed": pack["execution_allowed"],
        "executed": pack["executed"],
        "non_authoritative": pack["non_authoritative"],
        "evidence_required": pack["evidence_required"],
        "report_required": pack["report_required"],
    }
    _assert_non_executing_invariants(final_output)
    serialized = json.dumps({"routed": routed, "pack": pack, "final_output": final_output}, sort_keys=True)
    assert "telegram_summary" in final_output
    assert "authorization: bearer" not in serialized.lower()
    assert "token=" not in serialized.lower()
    assert "password=" not in serialized.lower()
    assert "execution_allowed\": true" not in serialized.lower()
    _assert_no_raw_artifact_slots(pack)
    _assert_no_raw_artifact_slots(final_output)
