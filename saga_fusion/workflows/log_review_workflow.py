from __future__ import annotations

import re
from pathlib import Path
from .secret_audit_workflow import SECRET_PATTERNS, redact_secret_text
from .workflow_types import WorkflowCategory, WorkflowPlan, WorkflowRisk, WorkflowTemplate, list_text_files, read_small, workflow_step

LOG_NAMES = (".log", ".jsonl", ".out", ".err")
ERROR_PATTERN = re.compile(r"(?i)\b(error|exception|traceback|failed|denied|unauthorized|critical)\b")


def redact_log_line(line: str) -> str:
    redacted = line
    for pattern in SECRET_PATTERNS.values():
        match = pattern.search(redacted)
        if match:
            value = match.group(match.lastindex or 0) if match.lastindex else match.group(0)
            redacted = redacted.replace(value, redact_secret_text(value))
    redacted = re.sub(r"(?i)(token|secret|password|api[_-]?key)(\s*[:=]\s*)([^\s,'\"]+)", r"\1\2[REDACTED]", redacted)
    return redacted


def log_review_template() -> WorkflowTemplate:
    return WorkflowTemplate(
        workflow_id="log_review",
        name="Log Defensive Review",
        category=WorkflowCategory.LOG_REVIEW,
        default_risk=WorkflowRisk.R2,
        allowed_mode="evidence_only_redacted",
        required_inputs=("log_path",),
        description="Plan log scope review, error-pattern analysis, secret redaction, and anomaly summary.",
        tags=("logs", "redaction", "anomaly_summary"),
        steps=(
            workflow_step("log_scope", "Log scope", "Validate local log file/directory scope.", ("log_files",)),
            workflow_step("error_patterns", "Error patterns", "Count error and denial patterns.", ("error_events",)),
            workflow_step("secret_redaction", "Secret redaction", "Redact secret-like values before evidence/report output.", ("redacted_samples",)),
            workflow_step("anomaly_summary", "Anomaly summary", "Summarize anomalies without real containment.", ("anomaly_summary",)),
        ),
        execution_allowed=False,
    )


def generate_log_review_plan(log_path: str | Path, **inputs) -> WorkflowPlan:
    root = Path(log_path)
    if root.is_file():
        files = [root]
        base = root.parent
    else:
        files = [p for p in list_text_files(root) if p.suffix in LOG_NAMES]
        base = root
    errors = []
    redacted_samples = []
    for path in files:
        text = read_small(path)
        for line_no, line in enumerate(text.splitlines(), 1):
            if ERROR_PATTERN.search(line):
                errors.append({"file": str(path.relative_to(base)), "line": line_no, "sample": redact_log_line(line)[:160]})
            if any(pattern.search(line) for pattern in SECRET_PATTERNS.values()) and len(redacted_samples) < 20:
                redacted_samples.append({"file": str(path.relative_to(base)), "line": line_no, "sample": redact_log_line(line)[:160]})
    evidence = {
        "log_files": [str(p.relative_to(base)) for p in files],
        "error_events": errors,
        "redacted_samples": redacted_samples,
        "anomaly_summary": {"error_count": len(errors), "secret_like_lines_redacted": len(redacted_samples)},
        "execution_allowed": False,
    }
    return log_review_template().build_plan(inputs={"log_path": str(root), **inputs}, evidence=evidence, notes=("redacted_output_only",))
