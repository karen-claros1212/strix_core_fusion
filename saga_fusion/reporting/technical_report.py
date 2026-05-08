from __future__ import annotations

import json
from dataclasses import asdict

from .report_redactor import ReportRedactor
from .report_types import MissionReport


class TechnicalReport:
    def __init__(self, redactor: ReportRedactor | None = None):
        self.redactor = redactor or ReportRedactor()

    def render(self, report: MissionReport) -> str:
        lines = [f'# {report.title}', '', '## Methodology', 'Dry-run gated STRIX/Saga Fusion reporting with evidence preservation.', '']
        for section in report.sections:
            lines.append(f'## {section.title}')
            content = self.redactor.redact(section.content)
            lines.append(json.dumps(content, indent=2, sort_keys=True) if isinstance(content, (dict, list)) else str(content))
            lines.append('')
        if report.artifacts:
            lines.append('## Artifacts')
            for artifact in report.artifacts:
                lines.append(f'- `{artifact.path}` — {artifact.description}')
        lines.append('## Tests Executed')
        lines.append('- See phase validation logs and report metadata.')
        return self.redactor.redact('\n'.join(lines))
