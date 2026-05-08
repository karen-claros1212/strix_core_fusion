from __future__ import annotations

import re
from pathlib import Path
from .workflow_types import WorkflowCategory, WorkflowPlan, WorkflowRisk, WorkflowTemplate, list_text_files, read_small, workflow_step

SECRET_PATTERNS = {
    "generic_assignment": re.compile(r"(?i)\b(api[_-]?key|token|secret|password)\b\s*[:=]\s*['\"]?([^'\"\s]{8,})"),
    "private_key": re.compile(r"-----BEGIN [A-Z ]*" + r"PRIV" + r"ATE KEY-----"),
    "bearer": re.compile(r"(?i)bearer\s+([a-z0-9._\-]{12,})"),
}
FIXTURE_HINTS = ("example", "placeholder", "dummy", "test", "fixture", "fake", "changeme", "redacted")


def redact_secret_text(text: str) -> str:
    if not text:
        return ""
    return "[REDACTED]"


def secret_audit_template() -> WorkflowTemplate:
    return WorkflowTemplate(
        workflow_id="secret_audit",
        name="Secret Exposure Audit",
        category=WorkflowCategory.SECRET_AUDIT,
        default_risk=WorkflowRisk.R3,
        allowed_mode="evidence_only_redacted",
        required_inputs=("repo_path",),
        description="Plan secret-pattern scan, fixture classification, evidence capture, and remediation recommendation.",
        tags=("secrets", "redaction", "dry_run"),
        steps=(
            workflow_step("scan_patterns", "Scan patterns", "Locate secret-like patterns in small text files.", ("pattern_matches",)),
            workflow_step("classify_fixture_vs_real", "Classify fixture vs real", "Classify matches as fixture/placeholder or needs-review without exposing values.", ("classifications",)),
            workflow_step("evidence", "Evidence", "Record only redacted snippets and file/line metadata.", ("redacted_evidence",)),
            workflow_step("remediation_recommendation", "Remediation recommendation", "Recommend rotation/removal via manual review only.", ("recommendations",)),
            workflow_step("no_full_secret_exposure", "No full secret exposure", "Ensure reports never contain complete secret values.", ("redacted",)),
        ),
        execution_allowed=False,
    )


def generate_secret_audit_plan(repo_path: str | Path, **inputs) -> WorkflowPlan:
    root = Path(repo_path)
    findings = []
    for path in list_text_files(root):
        rel = str(path.relative_to(root))
        text = read_small(path)
        for line_no, line in enumerate(text.splitlines(), 1):
            for pattern_name, pattern in SECRET_PATTERNS.items():
                match = pattern.search(line)
                if not match:
                    continue
                value = match.group(match.lastindex or 0) if match.lastindex else match.group(0)
                lowered = " ".join([rel, line, value]).lower()
                classification = "fixture_or_placeholder" if any(hint in lowered for hint in FIXTURE_HINTS) else "needs_manual_review"
                findings.append({
                    "file": rel,
                    "line": line_no,
                    "pattern": pattern_name,
                    "classification": classification,
                    "redacted_value": redact_secret_text(value),
                    "recommendation": "Keep fixture redacted" if classification.startswith("fixture") else "Manually verify, rotate if real, and remove from tracked files.",
                })
    evidence = {"findings": findings, "finding_count": len(findings), "redacted": True, "execution_allowed": False}
    return secret_audit_template().build_plan(inputs={"repo_path": str(root), **inputs}, evidence=evidence, notes=("no_full_secret_exposure",))
