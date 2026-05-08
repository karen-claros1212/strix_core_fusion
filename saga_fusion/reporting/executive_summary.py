from __future__ import annotations

from .report_types import MissionReport
from .report_redactor import ReportRedactor


class ExecutiveSummary:
    def __init__(self, redactor: ReportRedactor | None = None):
        self.redactor = redactor or ReportRedactor()

    def render(self, report: MissionReport) -> str:
        risk = next((s.content for s in report.sections if s.name == 'risk_overview'), {})
        approvals = next((s.content for s in report.sections if s.name == 'approvals'), [])
        findings = next((s.content for s in report.sections if s.name == 'findings'), [])
        has_r4 = any(str(a.get('risk_level','')).upper() == 'R4' or a.get('approval_id') for a in approvals if isinstance(a, dict))
        has_r5 = any(str(f.get('risk_level','')).upper() == 'R5' or str(f.get('status','')).lower() == 'blocked' for f in findings if isinstance(f, dict))
        text = (
            f"Executive summary for {report.title}. "
            f"Findings: {len(findings or [])}. Impact: controlled under STRIX gates. "
            f"Top risks: {risk}. "
            f"R4 approval required: {'yes' if has_r4 else 'no'}. R5 blocked: {'yes' if has_r5 else 'no'}. "
            "Recommended actions: review findings, keep dry-run evidence, and apply approved remediation only. "
            "Residual risk: monitored."
        )
        return self.redactor.redact(text)
