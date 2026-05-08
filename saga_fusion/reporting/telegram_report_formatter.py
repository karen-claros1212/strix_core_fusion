from __future__ import annotations

from .executive_summary import ExecutiveSummary
from .report_redactor import ReportRedactor
from .report_types import MissionReport


class TelegramReportFormatter:
    def __init__(self, max_length: int = 3500, redactor: ReportRedactor | None = None):
        self.max_length = max_length
        self.redactor = redactor or ReportRedactor()
        self.executive = ExecutiveSummary(self.redactor)

    def format(self, report: MissionReport, artifact_ref: str | None = None) -> str:
        text = self.executive.render(report)
        approvals = next((s.content for s in report.sections if s.name == 'approvals'), [])
        pending = [a for a in approvals or [] if isinstance(a, dict) and a.get('status') == 'PENDING']
        if pending:
            text += f"\nPending approvals: {len(pending)}"
        if artifact_ref:
            text += f"\nArtifact: {artifact_ref}"
        text = self.redactor.redact(text)
        if len(text) > self.max_length:
            suffix = f"\nArtifact: {artifact_ref}" if artifact_ref else ''
            text = text[: max(0, self.max_length - len(suffix) - 20)] + '… [truncated]' + suffix
        return text
