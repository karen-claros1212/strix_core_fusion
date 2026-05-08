from __future__ import annotations

from .workflow_types import WorkflowCategory, WorkflowPlan, WorkflowRisk, WorkflowTemplate, workflow_step


def incident_response_triage_template() -> WorkflowTemplate:
    return WorkflowTemplate(
        workflow_id="incident_response_triage",
        name="Incident Response Triage Plan",
        category=WorkflowCategory.INCIDENT_RESPONSE,
        default_risk=WorkflowRisk.R4,
        allowed_mode="plan_only_no_containment",
        required_inputs=("incident_summary",),
        description="Plan triage, containment, evidence preservation, eradication, recovery, and post-incident actions without real containment.",
        tags=("incident_response", "triage", "plan_only"),
        steps=(
            workflow_step("triage", "Triage", "Classify incident scope, affected systems, and urgency.", ("triage",)),
            workflow_step("containment_plan", "Containment plan", "Draft containment plan for human approval; do not isolate systems.", ("containment_plan",)),
            workflow_step("evidence_preservation", "Evidence preservation", "Identify evidence to preserve with chain-of-custody notes.", ("evidence_preservation",)),
            workflow_step("eradication_plan", "Eradication plan", "Plan eradication tasks for later approved execution.", ("eradication_plan",)),
            workflow_step("recovery_plan", "Recovery plan", "Plan recovery and validation steps.", ("recovery_plan",)),
            workflow_step("post_incident_actions", "Post-incident actions", "Plan lessons learned and control improvements.", ("post_incident_actions",)),
            workflow_step("no_real_containment", "No real containment", "Do not block accounts, stop services, or modify hosts automatically.", ("execution_allowed",)),
        ),
        execution_allowed=False,
    )


def generate_incident_response_plan(incident_summary: str, **inputs) -> WorkflowPlan:
    evidence = {
        "triage": {"summary": incident_summary, "status": "triage_plan_only"},
        "containment_plan": ["Identify isolation candidates", "Prepare approval request", "Do not perform containment in this workflow"],
        "evidence_preservation": ["Preserve logs", "Record timestamps", "Hash artifacts if collected by approved process"],
        "eradication_plan": ["Root-cause review", "Patch plan", "Credential rotation plan if approved"],
        "recovery_plan": ["Restore service plan", "Validation plan", "Monitoring plan"],
        "post_incident_actions": ["Postmortem", "Detection updates", "Control backlog"],
        "execution_allowed": False,
    }
    return incident_response_triage_template().build_plan(inputs={"incident_summary": incident_summary, **inputs}, evidence=evidence, notes=("no_real_containment", "human_approval_required_for_actions"))
