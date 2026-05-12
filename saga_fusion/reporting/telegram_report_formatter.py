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

    def format_manifest_summary(self, manifest_summary: dict) -> str:
        """Render a Telegram-safe manifest summary: ids, refs, hashes, no raw artifact bodies."""
        summary = self.redactor.redact(manifest_summary or {})
        lines = [
            f"Manifest: {summary.get('manifest_id', 'unknown')}",
            f"Artifacts: {summary.get('artifact_count', 0)}",
            f"Non-authoritative: {summary.get('non_authoritative') is True}",
            f"Execution allowed: {summary.get('execution_allowed') is True}",
        ]
        for artifact in summary.get('artifacts', [])[:8]:
            if not isinstance(artifact, dict):
                continue
            locator = artifact.get('path') or artifact.get('ref') or 'unreferenced'
            digest = str(artifact.get('sha256', ''))[:12]
            lines.append(f"- {artifact.get('artifact_id')}: {locator} sha256={digest}… redaction={artifact.get('redaction_status')}")
        text = "\n".join(lines)
        if len(text) > self.max_length:
            text = text[: max(0, self.max_length - 20)] + '… [truncated]'
        return text

