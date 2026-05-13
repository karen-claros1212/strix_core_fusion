from __future__ import annotations

import hashlib
import json
import uuid
from typing import Any

from .defensive_workflow_types import DefensiveReportPack, DefensiveWorkflowPlan, DefensiveWorkflowReport, redact_obj, redact_text


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


    def build_report_pack(self, plan: DefensiveWorkflowPlan | dict) -> DefensiveReportPack:
        """Build a minimal Phase 10D report pack from existing workflow/report/manifest layers.

        The pack is reference-only: evidence/report artifacts are represented by
        inert refs, SHA-256 values, and manifest summaries, never raw artifact
        bodies or executable content.
        """
        payload = plan.to_dict() if hasattr(plan, "to_dict") else redact_obj(dict(plan or {}))
        from saga_fusion.reporting.report_redactor import ReportRedactor

        payload = ReportRedactor().redact(payload)
        self._assert_workflow_contract(payload)

        report = self.build_report(payload)
        report_payload = report.to_dict()
        workflow_category = self._workflow_category(str(payload.get("workflow_id", "unknown")))

        from saga_fusion.manifests import ManifestBuilder, RedactionStatus, ReportArtifactRef, SecretScanStatus

        manifest_builder = ManifestBuilder()
        evidence_metadata = self._evidence_metadata(payload)
        evidence_ref = manifest_builder.external_evidence_ref(
            ref=f"defensive-workflow://{workflow_category}/{payload.get('workflow_id', 'unknown')}/evidence-metadata",
            sha256=self._sha256(evidence_metadata),
            size_bytes=len(json.dumps(evidence_metadata, sort_keys=True).encode("utf-8")),
            artifact_id=f"evidence-{workflow_category}",
            category="defensive_workflow_evidence_metadata",
            source_phase="10D",
            classification="internal",
            risk=self._risk_level(payload),
            redaction_status=RedactionStatus.REDACTED.value,
            secret_scan_status=SecretScanStatus.CLEAN.value,
            provenance={"source": "DefensiveWorkflowPlan", "body_embedded": False},
            metadata={"workflow_category": workflow_category, "schema_version": "defensive_evidence_ref_v1"},
        )
        evidence_manifest = manifest_builder.build_evidence_manifest(
            [evidence_ref],
            source_phase="10D",
            metadata={"workflow_category": workflow_category, "body_embedded": False},
        )

        report_metadata = self._report_metadata(report_payload)
        report_ref = ReportArtifactRef(
            artifact_id=f"report-{workflow_category}",
            ref=f"defensive-report://{report.report_id}",
            category="defensive_report_pack_report",
            sha256=self._sha256(report_metadata),
            size_bytes=len(json.dumps(report_metadata, sort_keys=True).encode("utf-8")),
            source_phase="10D",
            classification="internal",
            risk=self._risk_level(payload),
            redaction_status=RedactionStatus.REDACTED.value,
            secret_scan_status=SecretScanStatus.CLEAN.value,
            provenance={"source": "DefensiveWorkflowReporter", "body_embedded": False},
            metadata={"workflow_category": workflow_category, "schema_version": "defensive_report_ref_v1"},
            evidence_refs=(evidence_ref.artifact_id,),
        )
        reporting_manifest = manifest_builder.build_reporting_manifest(
            [report_ref],
            [evidence_ref],
            source_phase="10D",
            metadata={"workflow_category": workflow_category, "body_embedded": False},
        )

        technical_findings = self._technical_findings(payload)
        pack = DefensiveReportPack(
            pack_id=f"defensive-pack-{uuid.uuid4().hex[:12]}",
            workflow_category=workflow_category,
            workflow_id=str(payload.get("workflow_id", "unknown")),
            report_id=report.report_id,
            executive_summary=report.executive_summary,
            technical_findings=technical_findings,
            risk_classification=self._risk_classification(payload),
            recommended_actions=[redact_text(str(item)) for item in payload.get("recommendations", [])],
            containment_steps=self._containment_steps(payload),
            recovery_steps=self._recovery_steps(payload),
            lessons_learned=self._lessons_learned(payload),
            evidence_refs=[self._artifact_summary(evidence_ref)],
            report_refs=[self._report_ref_summary(report_ref)],
            manifest_refs=[
                self._manifest_summary(evidence_manifest, "evidence"),
                self._manifest_summary(reporting_manifest, "reporting"),
            ],
            metadata={
                "phase": "10d-2",
                "schema_version": "defensive_report_pack_v1",
                "active_redaction": True,
                "thin_aggregation_layer": True,
                "real_telegram_used": False,
                "real_llm_used": False,
                "real_tool_execution": False,
                "raw_artifact_bodies_embedded": False,
            },
        )
        return pack

    def _assert_workflow_contract(self, payload: dict[str, Any]) -> None:
        if payload.get("execution_allowed") is not False or payload.get("executed") is not False:
            raise ValueError("defensive report packs only accept non-executed plans")
        if payload.get("evidence_required") is not True or payload.get("report_required") is not True:
            raise ValueError("defensive report packs require evidence/report-required plans")
        if payload.get("non_authoritative") is not True:
            raise ValueError("defensive report packs must remain non-authoritative")

    @staticmethod
    def _sha256(value: Any) -> str:
        encoded = json.dumps(redact_obj(value), sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    @staticmethod
    def _workflow_category(workflow_id: str) -> str:
        for category in (
            "malware_triage",
            "ransomware_response",
            "phishing_attachment",
            "webshell_investigation",
            "credential_theft",
            "suspicious_process",
            "defense_status",
        ):
            if workflow_id.startswith(category.replace("_", "-")) or workflow_id == category:
                return category
        return workflow_id.split("-")[0].replace("-", "_") or "unknown"

    @staticmethod
    def _risk_level(payload: dict[str, Any]) -> str:
        category = str((payload.get("classification") or {}).get("category", "unknown")).lower()
        if category in {"ransomware", "stealer", "backdoor"}:
            return "R3"
        if category in {"trojan"}:
            return "R2"
        return "R1"

    def _risk_classification(self, payload: dict[str, Any]) -> dict[str, Any]:
        classification = payload.get("classification") or {}
        return redact_obj({
            "category": classification.get("category", "unknown"),
            "confidence": classification.get("confidence", 0),
            "risk": self._risk_level(payload),
            "summary": classification.get("defensive_summary") or classification.get("summary", "defensive triage only"),
            "execution_allowed": False,
            "non_authoritative": True,
        })

    def _technical_findings(self, payload: dict[str, Any]) -> dict[str, Any]:
        indicator_types: dict[str, int] = {}
        for indicator in payload.get("indicators", []) or []:
            kind = str(indicator.get("ioc_type") or indicator.get("type") or "unknown") if isinstance(indicator, dict) else "unknown"
            indicator_types[kind] = indicator_types.get(kind, 0) + 1
        return redact_obj({
            "workflow_id": payload.get("workflow_id"),
            "title": payload.get("title"),
            "mitre_ids": [item.get("technique_id") for item in payload.get("mitre_mappings", []) if isinstance(item, dict) and item.get("technique_id")],
            "indicator_count": len(payload.get("indicators", []) or []),
            "indicator_types": indicator_types,
            "yara_rule_count": len(payload.get("yara_rules", []) or []),
            "sigma_rule_count": len(payload.get("sigma_rules", []) or []),
            "checklist": payload.get("checklist", []),
            "evidence_reference_only": True,
            "raw_artifact_bodies_embedded": False,
            "execution_allowed": False,
            "non_authoritative": True,
        })

    def _evidence_metadata(self, payload: dict[str, Any]) -> dict[str, Any]:
        evidence = payload.get("evidence") or {}
        return redact_obj({
            "workflow_id": payload.get("workflow_id"),
            "classification": payload.get("classification"),
            "evidence_keys": sorted(str(key) for key in evidence.keys()),
            "indicator_count": len(payload.get("indicators", []) or []),
            "mitre_count": len(payload.get("mitre_mappings", []) or []),
            "report_required": True,
            "evidence_required": True,
            "execution_allowed": False,
            "body_embedded": False,
        })

    def _report_metadata(self, report_payload: dict[str, Any]) -> dict[str, Any]:
        return redact_obj({
            "report_id": report_payload.get("report_id"),
            "workflow_id": report_payload.get("workflow_id"),
            "redacted": report_payload.get("redacted") is True,
            "schema_version": report_payload.get("metadata", {}).get("schema_version"),
            "summary_sha256": self._sha256({
                "executive_summary": report_payload.get("executive_summary"),
                "telegram_summary": report_payload.get("telegram_summary"),
            }),
            "body_embedded": False,
        })

    @staticmethod
    def _artifact_summary(ref) -> dict[str, Any]:
        return redact_obj({
            "artifact_id": ref.artifact_id,
            "ref": ref.ref,
            "kind": ref.kind,
            "category": ref.category,
            "sha256": ref.sha256,
            "size_bytes": ref.size_bytes,
            "redaction_status": ref.redaction_status,
            "secret_scan_status": ref.secret_scan_status,
            "non_authoritative": True,
            "execution_allowed": False,
        })

    def _report_ref_summary(self, ref) -> dict[str, Any]:
        payload = self._artifact_summary(ref)
        payload["evidence_refs"] = list(ref.evidence_refs)
        return payload

    @staticmethod
    def _manifest_summary(manifest, kind: str) -> dict[str, Any]:
        return {
            "manifest_id": manifest.manifest_id,
            "kind": kind,
            "source_phase": manifest.source_phase,
            "artifact_count": len(getattr(manifest, "artifacts", ())) + len(getattr(manifest, "reports", ())) + len(getattr(manifest, "evidence_refs", ())),
            "non_authoritative": manifest.non_authoritative,
            "execution_allowed": manifest.execution_allowed,
            "version": manifest.version,
        }

    @staticmethod
    def _containment_steps(payload: dict[str, Any]) -> list[str]:
        playbook = payload.get("playbook") or {}
        steps = list(playbook.get("steps") or [])[:4]
        if not steps:
            steps = list(payload.get("checklist") or [])[:3]
        steps.append("Perform containment only through approved STRIX gates; this pack did not execute actions.")
        return [redact_text(str(item)) for item in steps]

    @staticmethod
    def _recovery_steps(payload: dict[str, Any]) -> list[str]:
        text = " ".join(json.dumps(payload.get(key, {}), sort_keys=True) for key in ("playbook", "recommendations", "checklist"))
        steps = ["Validate recovery using approved operational runbooks only."]
        if "backup" in text.lower() or "restore" in text.lower():
            steps.insert(0, "Review backup/restore readiness with system owners before any recovery operation.")
        if "credential" in text.lower() or "session" in text.lower():
            steps.insert(0, "Coordinate credential/session recovery through IAM owners and approved channels.")
        return [redact_text(step) for step in steps]

    @staticmethod
    def _lessons_learned(payload: dict[str, Any]) -> list[str]:
        workflow = payload.get("workflow_id", "defensive_workflow")
        lessons = [
            f"{workflow} remained evidence/report-only and non-authoritative.",
            "Evidence should stay reference-only with hashes and manifest metadata.",
            "Improve detections and runbooks through approved review, not automated execution.",
        ]
        return [redact_text(str(item)) for item in lessons]

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
