from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any, Iterable

from .hashing import file_size, sha256_file
from .policy import ManifestPolicy
from .redactor import ManifestRedactor
from .types import (
    EvidenceArtifactRef,
    EvidenceManifest,
    RedactionStatus,
    ReportArtifactRef,
    ReportingManifest,
    SecretScanStatus,
)
from .validator import ManifestValidator


class ManifestBuilder:
    """Builds inert references to evidence/report artifacts; it never executes artifacts."""

    def __init__(self, policy: ManifestPolicy | None = None, redactor: ManifestRedactor | None = None, validator: ManifestValidator | None = None):
        self.policy = policy or ManifestPolicy()
        self.redactor = redactor or ManifestRedactor()
        self.validator = validator or ManifestValidator(self.policy, self.redactor)

    def evidence_ref_from_path(self, path: str | Path, *, artifact_id: str | None = None, category: str = "evidence", source_phase: str = "unknown", mission_id: str | None = None, session_id: str | None = None, classification: str = "internal", risk: str = "R0", redaction_status: str | None = None, provenance: dict[str, Any] | None = None, references: Iterable[str] = (), metadata: dict[str, Any] | None = None) -> EvidenceArtifactRef:
        return self._ref_from_path(EvidenceArtifactRef, path, artifact_id=artifact_id, category=category, source_phase=source_phase, mission_id=mission_id, session_id=session_id, classification=classification, risk=risk, redaction_status=redaction_status, provenance=provenance, references=references, metadata=metadata)

    def report_ref_from_path(self, path: str | Path, *, artifact_id: str | None = None, category: str = "report", source_phase: str = "unknown", mission_id: str | None = None, session_id: str | None = None, classification: str = "internal", risk: str = "R0", redaction_status: str | None = None, provenance: dict[str, Any] | None = None, references: Iterable[str] = (), evidence_refs: Iterable[str] = (), metadata: dict[str, Any] | None = None) -> ReportArtifactRef:
        ref = self._ref_from_path(ReportArtifactRef, path, artifact_id=artifact_id, category=category, source_phase=source_phase, mission_id=mission_id, session_id=session_id, classification=classification, risk=risk, redaction_status=redaction_status, provenance=provenance, references=references, metadata=metadata, evidence_refs=tuple(evidence_refs))
        return ref

    def external_evidence_ref(self, *, ref: str, sha256: str, size_bytes: int | None = None, artifact_id: str | None = None, category: str = "evidence", source_phase: str = "unknown", mission_id: str | None = None, session_id: str | None = None, classification: str = "internal", risk: str = "R0", redaction_status: str | None = None, secret_scan_status: str = SecretScanStatus.NOT_SCANNED.value, provenance: dict[str, Any] | None = None, references: Iterable[str] = (), metadata: dict[str, Any] | None = None) -> EvidenceArtifactRef:
        return EvidenceArtifactRef(
            artifact_id=artifact_id or self._artifact_id("evidence"), ref=ref, category=category, sha256=sha256, size_bytes=size_bytes,
            source_phase=source_phase, mission_id=mission_id, session_id=session_id, classification=classification, risk=risk,
            redaction_status=redaction_status or self._default_redaction_status(classification, secret_scan_status), secret_scan_status=secret_scan_status,
            provenance=self.redactor.redact(provenance or {}), references=tuple(references), metadata=self.redactor.redact(metadata or {}),
        )

    def build_evidence_manifest(self, artifacts: Iterable[EvidenceArtifactRef], *, mission_id: str | None = None, session_id: str | None = None, source_phase: str = "unknown", metadata: dict[str, Any] | None = None, validate: bool = True) -> EvidenceManifest:
        manifest = EvidenceManifest(artifacts=tuple(artifacts), mission_id=mission_id, session_id=session_id, source_phase=source_phase, policy={"execution_allowed": False, "non_authoritative": True}, metadata=self.redactor.redact(metadata or {}))
        if validate:
            self.validator.assert_valid(manifest)
        return manifest

    def build_reporting_manifest(self, reports: Iterable[ReportArtifactRef], evidence_refs: Iterable[EvidenceArtifactRef], *, mission_id: str | None = None, session_id: str | None = None, source_phase: str = "unknown", metadata: dict[str, Any] | None = None, validate: bool = True) -> ReportingManifest:
        manifest = ReportingManifest(reports=tuple(reports), evidence_refs=tuple(evidence_refs), mission_id=mission_id, session_id=session_id, source_phase=source_phase, policy={"execution_allowed": False, "non_authoritative": True}, metadata=self.redactor.redact(metadata or {}))
        if validate:
            self.validator.assert_valid(manifest)
        return manifest

    def safe_summary(self, manifest: EvidenceManifest | ReportingManifest) -> dict[str, Any]:
        artifacts = list(getattr(manifest, "artifacts", ())) + list(getattr(manifest, "reports", ())) + list(getattr(manifest, "evidence_refs", ()))
        return {
            "manifest_id": manifest.manifest_id,
            "artifact_count": len(artifacts),
            "non_authoritative": manifest.non_authoritative,
            "execution_allowed": manifest.execution_allowed,
            "artifacts": [{key: getattr(artifact, key, None) for key in self.policy.safe_summary_keys} for artifact in artifacts],
        }

    def _ref_from_path(self, cls, path: str | Path, **kwargs):
        path = Path(path)
        text_sample = path.read_text(errors="ignore") if path.exists() and path.stat().st_size <= 512 * 1024 else ""
        secret_status = SecretScanStatus.SENSITIVE.value if text_sample and self.redactor.contains_secret(text_sample) else SecretScanStatus.CLEAN.value
        redaction_status = kwargs.pop("redaction_status") or self._default_redaction_status(kwargs.get("classification", "internal"), secret_status)
        return cls(
            artifact_id=kwargs.pop("artifact_id") or self._artifact_id(cls.__name__.replace("ArtifactRef", "").lower()),
            path=str(path),
            category=kwargs.pop("category"),
            sha256=sha256_file(path),
            size_bytes=file_size(path),
            source_phase=kwargs.pop("source_phase"),
            mission_id=kwargs.pop("mission_id"),
            session_id=kwargs.pop("session_id"),
            classification=kwargs.pop("classification"),
            risk=kwargs.pop("risk"),
            redaction_status=redaction_status,
            secret_scan_status=secret_status,
            provenance=self.redactor.redact(kwargs.pop("provenance") or {}),
            references=tuple(kwargs.pop("references")),
            metadata=self.redactor.redact(kwargs.pop("metadata") or {}),
            **kwargs,
        )

    def _default_redaction_status(self, classification: str, secret_scan_status: str) -> str:
        if str(classification).lower() in self.policy.sensitive_classifications or secret_scan_status == SecretScanStatus.SENSITIVE.value:
            return RedactionStatus.REFERENCE_ONLY.value
        return RedactionStatus.NOT_REQUIRED.value

    def _artifact_id(self, prefix: str) -> str:
        return f"{prefix}-{uuid.uuid4().hex[:12]}"
