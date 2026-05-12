from saga_fusion.reporting import EvidenceReporter, TelegramReportFormatter
from saga_fusion.manifests import ManifestBuilder


def test_evidence_reporter_builds_manifest_ref_without_content(tmp_path):
    path = tmp_path / "evidence.json"
    path.write_text('{"records": [{"token": "secret-value"}]}')

    ref = EvidenceReporter().build_manifest_ref(path, source_phase="8G")

    assert ref.path == str(path)
    assert "secret-value" not in repr(ref.to_dict())
    assert ref.sha256


def test_telegram_formatter_manifest_summary_is_safe(tmp_path):
    path = tmp_path / "evidence.txt"
    path.write_text("safe evidence")
    builder = ManifestBuilder()
    ref = builder.evidence_ref_from_path(path, artifact_id="ev1")
    manifest = builder.build_evidence_manifest([ref])

    text = TelegramReportFormatter(max_length=500).format_manifest_summary(builder.safe_summary(manifest))

    assert "Manifest:" in text
    assert str(path) in text
    assert "safe evidence" not in text
    assert "Execution allowed: False" in text
