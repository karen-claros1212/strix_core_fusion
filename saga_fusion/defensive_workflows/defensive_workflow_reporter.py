from __future__ import annotations

import json
import uuid

from .defensive_workflow_types import DefensiveWorkflowPlan, DefensiveWorkflowReport, redact_obj, redact_text


class DefensiveWorkflowReporter:
    """Render redacted defensive workflow reports for multiple audiences."""

    def build_report(self, plan: DefensiveWorkflowPlan | dict) -> DefensiveWorkflowReport:
        payload = plan.to_dict() if hasattr(plan, "to_dict") else redact_obj(dict(plan or {}))
        workflow_id = payload.get("workflow_id", "unknown")
        title = payload.get("title", "Defensive Workflow")
        summary = payload.get("summary", "")
        recommendations = payload.get("recommendations", [])
        technical = {
            "workflow_id": workflow_id,
            "classification": payload.get("classification", {}),
            "mitre_mappings": payload.get("mitre_mappings", []),
            "indicators": payload.get("indicators", []),
            "evidence": payload.get("evidence", {}),
            "yara_rules": payload.get("yara_rules", []),
            "sigma_rules": payload.get("sigma_rules", []),
            "checklist": payload.get("checklist", []),
            "recommendations": recommendations,
            "execution_allowed": False,
            "non_authoritative": True,
        }
        executive_summary = redact_text(
            f"{title}: {summary} Evidence/report required. Execution allowed: False. Recommendations: "
            + "; ".join(str(r) for r in recommendations[:3])
        )
        technical_report = redact_text(json.dumps(redact_obj(technical), indent=2, sort_keys=True))
        telegram_summary = self.telegram_summary(payload)
        return DefensiveWorkflowReport(
            report_id=f"defensive-report-{uuid.uuid4().hex[:12]}",
            workflow_id=workflow_id,
            executive_summary=executive_summary,
            technical_report=technical_report,
            telegram_summary=telegram_summary,
            redacted=True,
            non_authoritative=True,
            execution_allowed=False,
            metadata={"phase": "10b", "active_redaction": True, "schema_version": "defensive_workflow_report_v1"},
        )

    def telegram_summary(self, plan: DefensiveWorkflowPlan | dict) -> str:
        payload = plan.to_dict() if hasattr(plan, "to_dict") else redact_obj(dict(plan or {}))
        text = "\n".join([
            f"STRIX defensive workflow: {payload.get('title', 'unknown')}",
            f"Workflow: {payload.get('workflow_id', 'unknown')}",
            "Execution allowed: False",
            f"Evidence required: {payload.get('evidence_required') is True}",
            f"Report required: {payload.get('report_required') is True}",
            "Non-authoritative: True",
            "Next: review evidence and recommendations through approved STRIX gates.",
        ])
        return redact_text(text[:1800])
