from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from pathlib import Path

SEVERITY_ORDER = {"CRITICAL": 5, "HIGH": 4, "MEDIUM": 3, "LOW": 2, "INFO": 1}


@dataclass
class TriageFinding:
    finding_id: str
    title: str
    file: str
    line: int
    category: str
    severity: str
    confidence: str
    exploitability: str
    impact: str
    remediation_complexity: str
    evidence: str
    false_positive_likelihood: str
    recommended_action: str
    auto_fix_safe: bool
    requires_manual_review: bool
    priority: str
    finding_type: str
    dedupe_key: str
    source_count: int = 1

    def to_dict(self) -> dict:
        return asdict(self)


class FindingsTriage:
    def __init__(self, evidence_path: str | Path):
        self.evidence_path = Path(evidence_path)
        self.raw = json.loads(self.evidence_path.read_text())
        self.findings = self.raw.get("findings", [])

    def triage(self) -> list[TriageFinding]:
        grouped: dict[str, list[dict]] = {}
        for finding in self.findings:
            grouped.setdefault(self._dedupe_key(finding), []).append(finding)
        normalized: list[TriageFinding] = []
        for key, items in sorted(grouped.items()):
            normalized.append(self._normalize_group(key, items))
        return sorted(normalized, key=lambda item: (-SEVERITY_ORDER[item.severity], item.priority, item.finding_id))

    def matrix(self) -> dict:
        findings = self.triage()
        severity_counts = {level: 0 for level in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]}
        priority_counts = {level: 0 for level in ["P0", "P1", "P2", "P3"]}
        auto_fix_safe = 0
        manual_review = 0
        for finding in findings:
            severity_counts[finding.severity] += 1
            priority_counts[finding.priority] += 1
            auto_fix_safe += int(finding.auto_fix_safe)
            manual_review += int(finding.requires_manual_review)
        return {
            "source_evidence": str(self.evidence_path),
            "original_count": len(self.findings),
            "deduplicated_count": len(findings),
            "severity_counts": severity_counts,
            "priority_counts": priority_counts,
            "auto_fix_safe": auto_fix_safe,
            "manual_review": manual_review,
            "findings": [finding.to_dict() for finding in findings],
        }

    def _dedupe_key(self, finding: dict) -> str:
        path = finding.get("path", "")
        evidence = finding.get("evidence", "")
        category = finding.get("category", "")
        if path == ".env.example":
            return "env-example-placeholder"
        if path.startswith("reports/"):
            return "historical-report-secret-placeholder"
        if path.startswith("tests/") and category == "secret_scan":
            return "test-secret-fixtures"
        if path.startswith("tests/") and category == "config_audit":
            return "test-config-fixtures"
        if path.startswith("saga_fusion/") and ("REDACTED" in evidence or "bot_token" in evidence or "api_key" in evidence):
            return "redaction-code-self-hit"
        return f"{category}:{path}:{finding.get('line', 0)}"

    def _normalize_group(self, key: str, items: list[dict]) -> TriageFinding:
        first = items[0]
        title = first.get("title", "Finding")
        path = first.get("path", "")
        line = int(first.get("line", 0) or 0)
        evidence = first.get("evidence", "")
        category = first.get("category", "")
        if key == "env-example-placeholder":
            return self._finding(key, "Environment placeholder flagged as secret-like text", path, line, category, "INFO", "HIGH", "NONE", "LOW", "LOW", evidence, "HIGH", "Keep placeholder blank; optionally refine scanner allowlist for .env.example keys.", True, False, "P3", "secret handling", len(items))
        if key == "historical-report-secret-placeholder":
            return self._finding(key, "Historical report placeholder/diagnostic text flagged", path, line, category, "INFO", "MEDIUM", "NONE", "LOW", "LOW", evidence, "HIGH", "Keep audit history, but refine scanner to ignore already-redacted report text or mark as documentation drift.", False, True, "P3", "documentation drift", len(items))
        if key == "test-secret-fixtures":
            return self._finding(key, "Test secret fixture/redaction assertion flagged", path, line, category, "INFO", "HIGH", "NONE", "LOW", "LOW", evidence, "HIGH", "Keep test fixtures; ensure values are synthetic and scanner labels them as fixtures.", False, True, "P3", "weak test coverage", len(items))
        if key == "test-config-fixtures":
            return self._finding(key, "Test config fixture flagged as insecure config", path, line, category, "INFO", "HIGH", "NONE", "LOW", "LOW", evidence, "HIGH", "Keep fixture; add fixture-aware classification to scanner.", True, False, "P3", "weak test coverage", len(items))
        if key == "redaction-code-self-hit":
            return self._finding(key, "Secret redaction implementation self-hit", path, line, category, "LOW", "HIGH", "LOW", "LOW", "LOW", evidence, "MEDIUM", "Refine scanner to distinguish redaction patterns from real secrets; retain manual review for redaction code changes.", False, True, "P2", "logging/evidence leakage", len(items))
        severity = self._map_severity(first.get("severity", "LOW"))
        priority = "P1" if severity in {"CRITICAL", "HIGH"} else "P2" if severity == "MEDIUM" else "P3"
        return self._finding(key, title, path, line, category, severity, "MEDIUM", "LOW", "MEDIUM", "MEDIUM", evidence, "MEDIUM", first.get("recommendation", "Review and remediate if confirmed."), False, True, priority, self._type_for(category), len(items))

    def _finding(self, key, title, file, line, category, severity, confidence, exploitability, impact, complexity, evidence, fp, action, auto, manual, priority, finding_type, count):
        digest = hashlib.sha1(key.encode("utf-8")).hexdigest()[:8]
        return TriageFinding(
            finding_id=f"6C2-{digest}", title=title, file=file, line=line, category=category,
            severity=severity, confidence=confidence, exploitability=exploitability, impact=impact,
            remediation_complexity=complexity, evidence=evidence, false_positive_likelihood=fp,
            recommended_action=action, auto_fix_safe=auto, requires_manual_review=manual,
            priority=priority, finding_type=finding_type, dedupe_key=key, source_count=count,
        )

    def _map_severity(self, severity: str) -> str:
        value = (severity or "LOW").upper()
        return {"HIGH": "HIGH", "MED": "MEDIUM", "MEDIUM": "MEDIUM", "LOW": "LOW", "INFO": "INFO", "CRITICAL": "CRITICAL"}.get(value, "LOW")

    def _type_for(self, category: str) -> str:
        return {
            "secret_scan": "secret handling",
            "config_audit": "dependency/config risk",
            "docker_audit": "sandbox escape risk",
        }.get(category, "error handling")
