from __future__ import annotations

from dataclasses import dataclass, field

from .types import RedactionStatus, SecretScanStatus


@dataclass(frozen=True)
class ManifestPolicy:
    allowed_redaction_statuses_for_sensitive: tuple[str, ...] = (
        RedactionStatus.REDACTED.value,
        RedactionStatus.REFERENCE_ONLY.value,
        RedactionStatus.BLOCKED.value,
    )
    sensitive_classifications: tuple[str, ...] = ("sensitive", "secret", "restricted", "credentialed")
    enforce_non_authoritative: bool = True
    enforce_no_execution: bool = True
    require_sha256: bool = True
    require_redaction_for_sensitive: bool = True
    verify_existing_paths: bool = True
    blocked_metadata_keys: tuple[str, ...] = ("body", "content", "raw", "raw_body", "text")
    safe_summary_keys: tuple[str, ...] = field(default=("artifact_id", "path", "ref", "kind", "category", "sha256", "size_bytes", "redaction_status", "secret_scan_status"))

    def is_sensitive_artifact(self, artifact) -> bool:
        classification = str(getattr(artifact, "classification", "")).lower()
        secret_scan_status = str(getattr(artifact, "secret_scan_status", "")).lower()
        return classification in self.sensitive_classifications or secret_scan_status in {
            SecretScanStatus.SENSITIVE.value,
            SecretScanStatus.BLOCKED.value,
        }
