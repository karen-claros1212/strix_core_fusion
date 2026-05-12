import inspect
import json

import pytest

from saga_fusion.manifests import (
    EvidenceArtifactRef,
    ManifestBuilder,
    ManifestValidator,
    RedactionStatus,
    ReportArtifactRef,
    SecretScanStatus,
    sha256_file,
)
from saga_fusion.reporting import ReportRedactor


def test_valid_manifest_accepted(tmp_path):
    artifact = tmp_path / "evidence.json"
    artifact.write_text(json.dumps({"records": [{"event_type": "dry_run"}]}))
    builder = ManifestBuilder()

    ref = builder.evidence_ref_from_path(artifact, source_phase="8G", mission_id="m1")
    manifest = builder.build_evidence_manifest([ref], mission_id="m1", source_phase="8G")
    result = ManifestValidator().validate(manifest)

    assert result.ok
    assert manifest.non_authoritative is True
    assert manifest.execution_allowed is False
    assert ref.sha256 == sha256_file(artifact)
    assert ref.size_bytes == artifact.stat().st_size


def test_missing_or_invalid_artifact_hash_rejected(tmp_path):
    artifact = tmp_path / "evidence.txt"
    artifact.write_text("safe")
    ref = EvidenceArtifactRef(artifact_id="ev1", path=str(artifact), sha256="bad", size_bytes=4)
    manifest = ManifestBuilder().build_evidence_manifest([ref], validate=False)

    result = ManifestValidator().validate(manifest)

    assert not result.ok
    assert any("invalid sha256" in error for error in result.errors)


def test_secret_bearing_artifact_content_not_embedded(tmp_path):
    artifact = tmp_path / "secrets.log"
    artifact.write_text("Authorization: Bearer abc.def.ghi")
    builder = ManifestBuilder()

    ref = builder.evidence_ref_from_path(artifact, classification="sensitive", redaction_status=RedactionStatus.REDACTED.value)
    manifest = builder.build_evidence_manifest([ref])
    payload = manifest.to_dict()

    assert "abc.def.ghi" not in repr(payload)
    assert payload["artifacts"][0]["path"] == str(artifact)
    assert "content" not in payload["artifacts"][0]
    assert "body" not in payload["artifacts"][0]


def test_redaction_status_required_for_sensitive_artifacts(tmp_path):
    artifact = tmp_path / "sensitive.txt"
    artifact.write_text("TELEGRAM_BOT_TOKEN=" + "123456789:" + "ABCDEFGHIJKLMNOPQRSTUVwx-yz")
    ref = EvidenceArtifactRef(
        artifact_id="ev-sensitive",
        path=str(artifact),
        sha256=sha256_file(artifact),
        size_bytes=artifact.stat().st_size,
        classification="sensitive",
        redaction_status=RedactionStatus.NOT_REQUIRED.value,
        secret_scan_status=SecretScanStatus.SENSITIVE.value,
    )
    manifest = ManifestBuilder().build_evidence_manifest([ref], validate=False)

    result = ManifestValidator().validate(manifest)

    assert not result.ok
    assert any("requires redaction_status" in error for error in result.errors)


def test_builder_does_not_read_artifact_text_for_secret_scanning(tmp_path, monkeypatch):
    artifact = tmp_path / "secret_like.txt"
    artifact.write_text("Authorization: Bearer abc.def.ghi")

    def fail_read_text(self, *args, **kwargs):
        raise AssertionError("ManifestBuilder must not read/decode artifact text")

    monkeypatch.setattr(type(artifact), "read_text", fail_read_text)

    ref = ManifestBuilder().evidence_ref_from_path(artifact)

    assert ref.sha256 == sha256_file(artifact)
    assert ref.size_bytes == artifact.stat().st_size
    assert ref.secret_scan_status == SecretScanStatus.NOT_SCANNED.value
    assert ref.redaction_status == RedactionStatus.NOT_REQUIRED.value


def test_builder_uses_explicit_secret_scan_status_without_content_scan(tmp_path, monkeypatch):
    artifact = tmp_path / "declared_sensitive.txt"
    artifact.write_text("operator-declared sensitive artifact")

    def fail_read_text(self, *args, **kwargs):
        raise AssertionError("ManifestBuilder must not read/decode artifact text")

    monkeypatch.setattr(type(artifact), "read_text", fail_read_text)

    ref = ManifestBuilder().evidence_ref_from_path(
        artifact,
        secret_scan_status=SecretScanStatus.SENSITIVE.value,
        redaction_status=RedactionStatus.REDACTED.value,
    )
    manifest = ManifestBuilder().build_evidence_manifest([ref])

    assert ref.secret_scan_status == SecretScanStatus.SENSITIVE.value
    assert ManifestValidator().validate(manifest).ok


def test_artifact_refs_use_path_reference_not_raw_body(tmp_path):
    artifact = tmp_path / "evidence.txt"
    artifact.write_text("safe")
    builder = ManifestBuilder()
    ref = builder.evidence_ref_from_path(artifact)

    assert ref.path == str(artifact)
    assert not hasattr(ref, "body")
    assert not hasattr(ref, "content")
    with pytest.raises(ValueError):
        EvidenceArtifactRef(artifact_id="bad", path=str(artifact), sha256=sha256_file(artifact), metadata={"content": "raw"})


def test_non_authoritative_and_execution_allowed_false_enforced(tmp_path):
    artifact = tmp_path / "evidence.txt"
    artifact.write_text("safe")
    good_sha = sha256_file(artifact)

    with pytest.raises(ValueError):
        EvidenceArtifactRef(artifact_id="ev1", path=str(artifact), sha256=good_sha, execution_allowed=True)
    with pytest.raises(ValueError):
        EvidenceArtifactRef(artifact_id="ev2", path=str(artifact), sha256=good_sha, non_authoritative=False)


def test_report_manifest_links_evidence_refs(tmp_path):
    evidence = tmp_path / "evidence.json"
    report = tmp_path / "report.md"
    evidence.write_text('{"records": []}')
    report.write_text("# Safe report\nEvidence: ev1")
    builder = ManifestBuilder()

    ev_ref = builder.evidence_ref_from_path(evidence, artifact_id="ev1", source_phase="8G")
    report_ref = builder.report_ref_from_path(report, artifact_id="rep1", evidence_refs=["ev1"], source_phase="8G")
    manifest = builder.build_reporting_manifest([report_ref], [ev_ref], source_phase="8G")

    assert ManifestValidator().validate(manifest).ok
    assert manifest.reports[0].evidence_refs == ("ev1",)


def test_report_manifest_rejects_missing_evidence_link(tmp_path):
    report = tmp_path / "report.md"
    report.write_text("# Safe")
    builder = ManifestBuilder()
    report_ref = builder.report_ref_from_path(report, artifact_id="rep1", evidence_refs=["missing"], source_phase="8G")
    manifest = builder.build_reporting_manifest([report_ref], [], validate=False)

    result = ManifestValidator().validate(manifest)

    assert not result.ok
    assert any("missing evidence artifact" in error for error in result.errors)


def test_tampered_artifact_hash_detection(tmp_path):
    artifact = tmp_path / "evidence.txt"
    artifact.write_text("original")
    ref = ManifestBuilder().evidence_ref_from_path(artifact)
    artifact.write_text("tampered")
    manifest = ManifestBuilder().build_evidence_manifest([ref], validate=False)

    result = ManifestValidator().validate(manifest)

    assert not result.ok
    assert any("sha256 mismatch" in error for error in result.errors)


def test_existing_report_redactor_reused_for_manifest_metadata(tmp_path):
    artifact = tmp_path / "evidence.txt"
    artifact.write_text("safe")
    token = "123456789:" + "ABCDEFGHIJKLMNOPQRSTUVwx-yz"
    ref = ManifestBuilder().evidence_ref_from_path(artifact, metadata={"note": f"token={token}"})

    assert token not in repr(ref.to_dict())
    assert ReportRedactor().redact(f"token={token}") == ref.metadata["note"]


def test_no_direct_execution_surface():
    import saga_fusion.manifests as manifests

    forbidden = {"execute", "run", "dispatch", "send", "call"}
    for name in manifests.__all__:
        obj = getattr(manifests, name)
        if inspect.isclass(obj) and getattr(obj, "__module__", "").startswith("saga_fusion.manifests"):
            methods = {member for member, _ in inspect.getmembers(obj, predicate=inspect.isfunction)}
            assert not (methods & forbidden), f"{name} exposes execution-like methods: {methods & forbidden}"
