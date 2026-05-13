from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Any
import re
import uuid

from .ioc_types import IoC, infer_ioc_type
from .mitre_mapper import MitreMapper
from .threat_types import ThreatClassification


@dataclass(frozen=True)
class ThreatReport:
    report_id: str
    title: str
    summary: str
    classification: dict[str, Any]
    mitre_mappings: list[dict[str, Any]]
    iocs: list[dict[str, Any]]
    recommendations: list[str]
    non_authoritative: bool = True
    execution_allowed: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ThreatReportBuilder:
    SECRET_PATTERNS = (
        re.compile(r"(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*[^\s,;]+"),
        re.compile(r"\b\d{6,}:[A-Za-z0-9_-]{20,}\b"),
    )

    def __init__(self, mitre_mapper: MitreMapper | None = None):
        self.mitre_mapper = mitre_mapper or MitreMapper()

    def build_report(self, title: str, classification: ThreatClassification | dict, behaviors=None, iocs=None, notes: str = "") -> ThreatReport:
        title = self._redact(title or "Threat Triage Report")
        notes = self._redact(notes or "")
        classification_payload = classification.to_dict() if hasattr(classification, "to_dict") else dict(classification or {})
        classification_payload = self._redact_obj(classification_payload)
        mappings = [m.to_dict() for m in self.mitre_mapper.map_behaviors(behaviors or [])]
        ioc_payloads = [self._ioc_to_dict(ioc) for ioc in (iocs or [])]
        report_id = f"threat-report-{uuid.uuid4().hex[:12]}"
        category = classification_payload.get("category", "unknown")
        summary = self._redact(f"Non-authoritative defensive triage for {category}. {notes}".strip())
        recommendations = [
            "Validate indicators against trusted telemetry before action.",
            "Use generated YARA/Sigma only as defensive detection templates.",
            "Route containment or remediation through approved STRIX R4/SandboxController workflows.",
        ]
        return ThreatReport(
            report_id,
            title,
            summary,
            classification_payload,
            mappings,
            ioc_payloads,
            recommendations,
            True,
            False,
            {"schema_version": "10a", "defensive_only": True, "redacted": True, "execution_allowed": False},
        )

    def _ioc_to_dict(self, ioc) -> dict[str, Any]:
        if isinstance(ioc, IoC):
            payload = ioc.to_dict()
        else:
            value = str(ioc or "")
            payload = IoC(self._redact(value), infer_ioc_type(value)).to_dict()
        return self._redact_obj(payload)

    def _redact_obj(self, value):
        if isinstance(value, dict):
            return {k: self._redact_obj(v) for k, v in value.items()}
        if isinstance(value, list):
            return [self._redact_obj(v) for v in value]
        if isinstance(value, tuple):
            return [self._redact_obj(v) for v in value]
        if isinstance(value, str):
            return self._redact(value)
        return value

    def _redact(self, text: str) -> str:
        result = str(text or "")
        for pattern in self.SECRET_PATTERNS:
            result = pattern.sub(lambda m: m.group(1) + "=[REDACTED]" if m.lastindex else "[REDACTED]", result)
        return result[:5000]
