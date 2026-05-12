from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
import uuid


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ArtifactKind(str, Enum):
    EVIDENCE = "evidence"
    REPORT = "report"
    LOG = "log"
    SCREENSHOT = "screenshot"
    DATASET = "dataset"
    OTHER = "other"


class RedactionStatus(str, Enum):
    NOT_REQUIRED = "not_required"
    REDACTED = "redacted"
    REFERENCE_ONLY = "reference_only"
    BLOCKED = "blocked"


class SecretScanStatus(str, Enum):
    NOT_SCANNED = "not_scanned"
    CLEAN = "clean"
    SENSITIVE = "sensitive"
    BLOCKED = "blocked"


class ManifestValidationStatus(str, Enum):
    VALID = "valid"
    INVALID = "invalid"


@dataclass(frozen=True)
class ArtifactRefBase:
    artifact_id: str
    path: str | None = None
    ref: str | None = None
    kind: str = ArtifactKind.OTHER.value
    category: str = "general"
    sha256: str = ""
    size_bytes: int | None = None
    created_at: str = field(default_factory=utc_now)
    source_phase: str = "unknown"
    mission_id: str | None = None
    session_id: str | None = None
    classification: str = "internal"
    risk: str = "R0"
    redaction_status: str = RedactionStatus.NOT_REQUIRED.value
    secret_scan_status: str = SecretScanStatus.NOT_SCANNED.value
    provenance: dict[str, Any] = field(default_factory=dict)
    references: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)
    non_authoritative: bool = True
    execution_allowed: bool = False

    def __post_init__(self) -> None:
        if not self.path and not self.ref:
            raise ValueError("artifact refs require path or ref")
        if self.execution_allowed is not False:
            raise ValueError("manifest artifact refs must enforce execution_allowed=False")
        if self.non_authoritative is not True:
            raise ValueError("manifest artifact refs must enforce non_authoritative=True")
        forbidden = {"body", "content", "raw", "raw_body", "text"}
        if forbidden & set(self.metadata.keys()):
            raise ValueError("artifact metadata must not embed raw content/body")

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["references"] = list(self.references)
        return payload


@dataclass(frozen=True)
class EvidenceArtifactRef(ArtifactRefBase):
    kind: str = ArtifactKind.EVIDENCE.value


@dataclass(frozen=True)
class ReportArtifactRef(ArtifactRefBase):
    kind: str = ArtifactKind.REPORT.value
    evidence_refs: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        payload = super().to_dict()
        payload["evidence_refs"] = list(self.evidence_refs)
        return payload


@dataclass(frozen=True)
class EvidenceManifest:
    manifest_id: str = field(default_factory=lambda: f"evidence-manifest-{uuid.uuid4().hex[:12]}")
    artifacts: tuple[EvidenceArtifactRef, ...] = ()
    mission_id: str | None = None
    session_id: str | None = None
    source_phase: str = "unknown"
    created_at: str = field(default_factory=utc_now)
    policy: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    non_authoritative: bool = True
    execution_allowed: bool = False
    version: str = "8G-evidence-manifest-v1"

    def __post_init__(self) -> None:
        if self.execution_allowed is not False:
            raise ValueError("evidence manifests must enforce execution_allowed=False")
        if self.non_authoritative is not True:
            raise ValueError("evidence manifests must enforce non_authoritative=True")

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["artifacts"] = [artifact.to_dict() for artifact in self.artifacts]
        return payload


@dataclass(frozen=True)
class ReportingManifest:
    manifest_id: str = field(default_factory=lambda: f"reporting-manifest-{uuid.uuid4().hex[:12]}")
    reports: tuple[ReportArtifactRef, ...] = ()
    evidence_refs: tuple[EvidenceArtifactRef, ...] = ()
    mission_id: str | None = None
    session_id: str | None = None
    source_phase: str = "unknown"
    created_at: str = field(default_factory=utc_now)
    policy: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    non_authoritative: bool = True
    execution_allowed: bool = False
    version: str = "8G-reporting-manifest-v1"

    def __post_init__(self) -> None:
        if self.execution_allowed is not False:
            raise ValueError("reporting manifests must enforce execution_allowed=False")
        if self.non_authoritative is not True:
            raise ValueError("reporting manifests must enforce non_authoritative=True")

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["reports"] = [report.to_dict() for report in self.reports]
        payload["evidence_refs"] = [artifact.to_dict() for artifact in self.evidence_refs]
        return payload


@dataclass(frozen=True)
class ValidationResult:
    status: ManifestValidationStatus
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return self.status == ManifestValidationStatus.VALID

    def to_dict(self) -> dict[str, Any]:
        return {"status": self.status.value, "errors": list(self.errors), "warnings": list(self.warnings), "ok": self.ok}
