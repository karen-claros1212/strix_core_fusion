from __future__ import annotations

import json
import uuid
from pathlib import Path

from .report_redactor import ReportRedactor
from .report_types import MissionReport, ReportArtifact, ReportAudience, ReportSection


class ReportBuilder:
    def __init__(self, redactor: ReportRedactor | None = None):
        self.redactor = redactor or ReportRedactor()

    def build_mission_report(self, mission, findings=None, approvals=None, evidence=None, audience='technical') -> MissionReport:
        audience_enum = ReportAudience(audience)
        mission_data = self.redactor.redact(mission or {})
        findings_data = self.redactor.redact(findings or [])
        approvals_data = self.redactor.redact(approvals or [])
        evidence_data = self.redactor.redact(evidence or [])
        sections = [
            ReportSection('scope', 'Scope', {'mission': mission_data}),
            ReportSection('summary', 'Summary', self._summary(mission_data, findings_data, approvals_data)),
            ReportSection('risk_overview', 'Risk Overview', self._risk_overview(findings_data, approvals_data)),
            ReportSection('findings', 'Findings', findings_data),
            ReportSection('approvals', 'Approvals', approvals_data),
            ReportSection('actions', 'Actions', mission_data.get('actions', []) if isinstance(mission_data, dict) else []),
            ReportSection('evidence', 'Evidence', evidence_data),
            ReportSection('recommendations', 'Recommendations', self._recommendations(findings_data)),
            ReportSection('residual_risk', 'Residual Risk', {'status': 'controlled', 'notes': 'R4/R5 remain gated.'}),
        ]
        return MissionReport(str(uuid.uuid4()), audience_enum, f"Mission Report {mission_data.get('mission_id','unknown') if isinstance(mission_data, dict) else 'unknown'}", sections, [], {'schema_version': '7g'})

    def build_from_evidence(self, evidence_path, audience='technical') -> MissionReport:
        path = Path(evidence_path)
        evidence = []
        if path.exists():
            text = path.read_text(errors='ignore')
            if path.suffix == '.jsonl':
                for line in text.splitlines():
                    if line.strip():
                        evidence.append(json.loads(line))
            else:
                evidence = json.loads(text)
        report = self.build_mission_report({'mission_id': path.stem}, evidence=evidence, audience=audience)
        return MissionReport(report.report_id, report.audience, report.title, report.sections, [ReportArtifact(str(path), 'source evidence', 'application/json')], report.metadata)

    def build_findings_report(self, findings, audience='technical') -> MissionReport:
        return self.build_mission_report({'mission_id': 'findings'}, findings=findings, audience=audience)

    def _summary(self, mission, findings, approvals):
        return {'finding_count': len(findings or []), 'approval_count': len(approvals or []), 'status': mission.get('status','unknown') if isinstance(mission, dict) else 'unknown'}

    def _risk_overview(self, findings, approvals):
        severities = {}
        for finding in findings or []:
            sev = str(finding.get('severity','INFO')).upper() if isinstance(finding, dict) else 'INFO'
            severities[sev] = severities.get(sev, 0) + 1
        return {'severities': severities, 'pending_approvals': [a for a in approvals or [] if isinstance(a, dict) and a.get('status') == 'PENDING']}

    def _recommendations(self, findings):
        recs = []
        for finding in findings or []:
            if isinstance(finding, dict) and finding.get('recommendation'):
                recs.append(finding['recommendation'])
        return recs or ['Continue gated dry-run workflow and review residual risk.']
