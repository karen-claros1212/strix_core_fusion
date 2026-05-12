from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

from .hashing import sha256_file
from .policy import ManifestPolicy
from .redactor import ManifestRedactor
from .types import EvidenceManifest, ManifestValidationStatus, ReportingManifest, ValidationResult

_SHA256_RE = re.compile(r"^[a-f0-9]{64}$")


class ManifestValidator:
    def __init__(self, policy: ManifestPolicy | None = None, redactor: ManifestRedactor | None = None):
        self.policy = policy or ManifestPolicy()
        self.redactor = redactor or ManifestRedactor()

    def validate(self, manifest: EvidenceManifest | ReportingManifest) -> ValidationResult:
        errors: list[str] = []
        warnings: list[str] = []
        if self.policy.enforce_no_execution and getattr(manifest, "execution_allowed", None) is not False:
            errors.append("manifest execution_allowed must be false")
        if self.policy.enforce_non_authoritative and getattr(manifest, "non_authoritative", None) is not True:
            errors.append("manifest non_authoritative must be true")

        artifacts = list(getattr(manifest, "artifacts", ())) + list(getattr(manifest, "reports", ())) + list(getattr(manifest, "evidence_refs", ()))
        seen_ids: set[str] = set()
        for artifact in artifacts:
            self._validate_artifact(artifact, errors, warnings)
            artifact_id = getattr(artifact, "artifact_id", "")
            if artifact_id in seen_ids:
                warnings.append(f"duplicate artifact_id: {artifact_id}")
            seen_ids.add(artifact_id)

        if isinstance(manifest, ReportingManifest):
            evidence_ids = {artifact.artifact_id for artifact in manifest.evidence_refs}
            for report in manifest.reports:
                for evidence_ref in report.evidence_refs:
                    if evidence_ref not in evidence_ids:
                        errors.append(f"report {report.artifact_id} references missing evidence artifact {evidence_ref}")

        return ValidationResult(ManifestValidationStatus.INVALID if errors else ManifestValidationStatus.VALID, tuple(errors), tuple(warnings))

    def _validate_artifact(self, artifact, errors: list[str], warnings: list[str]) -> None:
        artifact_id = getattr(artifact, "artifact_id", "<unknown>")
        if not getattr(artifact, "path", None) and not getattr(artifact, "ref", None):
            errors.append(f"artifact {artifact_id} requires path or ref")
        if self.policy.enforce_no_execution and getattr(artifact, "execution_allowed", None) is not False:
            errors.append(f"artifact {artifact_id} execution_allowed must be false")
        if self.policy.enforce_non_authoritative and getattr(artifact, "non_authoritative", None) is not True:
            errors.append(f"artifact {artifact_id} non_authoritative must be true")
        sha = str(getattr(artifact, "sha256", ""))
        if self.policy.require_sha256 and not _SHA256_RE.match(sha):
            errors.append(f"artifact {artifact_id} has missing or invalid sha256")
        path_value = getattr(artifact, "path", None)
        if self.policy.verify_existing_paths and path_value:
            path = Path(path_value)
            if path.exists() and _SHA256_RE.match(sha):
                actual = sha256_file(path)
                if actual != sha:
                    errors.append(f"artifact {artifact_id} sha256 mismatch")
        if self.policy.is_sensitive_artifact(artifact):
            redaction_status = str(getattr(artifact, "redaction_status", ""))
            if self.policy.require_redaction_for_sensitive and redaction_status not in self.policy.allowed_redaction_statuses_for_sensitive:
                errors.append(f"artifact {artifact_id} requires redaction_status for sensitive artifact")
        metadata = getattr(artifact, "metadata", {}) or {}
        blocked = set(metadata.keys()) & set(self.policy.blocked_metadata_keys)
        if blocked:
            errors.append(f"artifact {artifact_id} embeds forbidden raw metadata keys: {sorted(blocked)}")
        serialized_metadata = repr(metadata)
        if self.redactor.contains_secret(serialized_metadata):
            errors.append(f"artifact {artifact_id} metadata contains secret-like content")

    def assert_valid(self, manifest: EvidenceManifest | ReportingManifest) -> None:
        result = self.validate(manifest)
        if not result.ok:
            raise ValueError("; ".join(result.errors))
