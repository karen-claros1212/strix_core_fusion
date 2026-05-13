from __future__ import annotations

import uuid
from typing import Any

from saga_fusion.defensive_workflows import DefensiveWorkflowKind, DefensiveWorkflowRegistry, DefensiveWorkflowReporter
from saga_fusion.defensive_workflows.defensive_workflow_types import redact_obj, redact_text

from .defensive_commands import DEFENSE_STATUS_COMMAND, DEFENSIVE_COMMANDS, parse_defensive_command, map_natural_language, known_defensive_commands
from .lab_mode import apply_lab_mode


class DefensiveCommandRouter:
    """Route Telegram defensive requests to Phase 10B workflows in lab/report-only mode."""

    def __init__(self, registry: DefensiveWorkflowRegistry | None = None, reporter: DefensiveWorkflowReporter | None = None):
        self.registry = registry or DefensiveWorkflowRegistry()
        self.reporter = reporter or DefensiveWorkflowReporter()

    def can_handle(self, text: str) -> bool:
        request = parse_defensive_command(text)
        if request is not None:
            return request.command in DEFENSIVE_COMMANDS
        return map_natural_language(text) is not None

    def route(self, text: str, *, chat_id: str = "", user_id: str = "") -> dict[str, Any]:
        request = parse_defensive_command(text) or map_natural_language(text)
        if request is None:
            return apply_lab_mode(
                {
                    "status": "clarification_required",
                    "clarification_required": True,
                    "blocked": True,
                    "reason": "no_defensive_workflow_selected",
                    "workflow_category": None,
                    "telegram_summary": "Indica un flujo defensivo: " + ", ".join(known_defensive_commands()),
                },
                artifact_ref="telegram:defensive-lab-clarification",
            )

        if request.blocked:
            return apply_lab_mode(
                {
                    **request.to_dict(),
                    "status": "blocked",
                    "blocked": True,
                    "workflow_category": None,
                    "telegram_summary": "Comando defensivo desconocido. No se ejecutó ninguna acción.",
                },
                artifact_ref="telegram:defensive-lab-blocked",
            )

        if request.command == DEFENSE_STATUS_COMMAND:
            workflows = [definition.workflow_id for definition in self.registry.list_workflows()]
            return apply_lab_mode(
                {
                    **request.to_dict(),
                    "status": "ok",
                    "workflow_category": "defense_status",
                    "available_workflows": workflows,
                    "telegram_summary": "STRIX defensa: modo laboratorio activo; análisis defensivo requiere evidencia y reporte; ejecución real deshabilitada.",
                    "recommendations": ["Usa comandos defensivos explícitos", "Adjunta solo referencias/metadata, no ejecutes archivos"],
                },
                artifact_ref="telegram:defensive-lab-status",
            )

        workflow_id = request.workflow_id or ""
        if self.registry.get(workflow_id) is None:
            return apply_lab_mode(
                {
                    **request.to_dict(),
                    "status": "blocked",
                    "blocked": True,
                    "workflow_category": workflow_id,
                    "reason": "unknown_defensive_workflow",
                    "telegram_summary": "Workflow defensivo desconocido. No se ejecutó ninguna acción.",
                },
                artifact_ref="telegram:defensive-lab-blocked",
            )

        plan = self._run_workflow(workflow_id, request.raw_text)
        report = self.reporter.build_report(plan)
        plan_payload = plan.to_dict()
        mitre = plan_payload.get("mitre_mappings", [])
        report_ref = f"reports/defensive_telegram/{report.report_id}.md"
        summary = self._telegram_summary(plan_payload, report.report_id, mitre)
        payload = {
            **request.to_dict(),
            "status": "workflow_plan",
            "blocked": False,
            "clarification_required": False,
            "workflow_category": workflow_id,
            "workflow_id": plan.workflow_id,
            "plan": plan_payload,
            "report_id": report.report_id,
            "artifact_ref": report_ref,
            "telegram_summary": summary,
            "mitre_mappings": mitre,
            "recommendations": plan_payload.get("recommendations", []),
            "raw_secret_display": False,
            "real_attachment_processing": False,
            "request_id": f"defensive-telegram-{uuid.uuid4().hex[:12]}",
        }
        return apply_lab_mode(redact_obj(payload), artifact_ref=report_ref)

    def _run_workflow(self, workflow_id: str, text: str):
        safe_text = redact_text(text)
        if workflow_id == DefensiveWorkflowKind.MALWARE_TRIAGE.value:
            return self.registry.run(workflow_id, observations=safe_text)
        if workflow_id == DefensiveWorkflowKind.RANSOMWARE_RESPONSE.value:
            return self.registry.run(workflow_id, incident_summary=safe_text, affected_scope="reported via Telegram metadata")
        if workflow_id == DefensiveWorkflowKind.PHISHING_ATTACHMENT.value:
            return self.registry.run(workflow_id, subject=safe_text, attachment_name="metadata_only", sender="reported_sender_alias")
        if workflow_id == DefensiveWorkflowKind.WEBSHELL_INVESTIGATION.value:
            return self.registry.run(workflow_id, web_root="reported_web_root_alias", suspicious_path="reported_path_alias")
        if workflow_id == DefensiveWorkflowKind.CREDENTIAL_THEFT.value:
            return self.registry.run(workflow_id, summary=safe_text, affected_identity="reported_identity_alias")
        if workflow_id == DefensiveWorkflowKind.SUSPICIOUS_PROCESS.value:
            return self.registry.run(workflow_id, process_name="reported_process_alias", command_line="", parent="", user="")
        return self.registry.run(workflow_id)

    @staticmethod
    def _telegram_summary(plan: dict[str, Any], report_id: str, mitre: list[dict[str, Any]]) -> str:
        mitre_ids = ", ".join(item.get("technique_id", "") for item in mitre[:4] if item.get("technique_id")) or "pending-validation"
        recommendations = plan.get("recommendations", [])[:3]
        lines = [
            f"STRIX defensa (lab): {plan.get('title', 'Defensive Workflow')}",
            f"Categoría: {plan.get('workflow_id', 'unknown')}",
            f"MITRE: {mitre_ids}",
            f"Reporte: {report_id}",
            "Ejecución real: False | Evidencia: requerida | Reporte: requerido",
            "Recomendaciones: " + "; ".join(str(item) for item in recommendations),
        ]
        return redact_text("\n".join(lines)[:1800])
