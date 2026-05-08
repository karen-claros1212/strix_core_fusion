from __future__ import annotations

from .config_audit_workflow import configuration_audit_template
from .dependency_audit_workflow import dependency_audit_template
from .docker_audit_workflow import docker_compose_audit_template
from .hardening_plan_workflow import hardening_plan_template
from .incident_response_workflow import incident_response_triage_template
from .log_review_workflow import log_review_template
from .repo_audit_workflow import repository_audit_template
from .secret_audit_workflow import secret_audit_template
from .workflow_types import WorkflowPlan, WorkflowTemplate


class DefensiveWorkflowRegistry:
    """Registry for defensive workflow templates; never executes workflows."""

    def __init__(self, templates: list[WorkflowTemplate] | None = None):
        self._templates: dict[str, WorkflowTemplate] = {}
        for template in templates or self.default_templates():
            self.register(template)

    @staticmethod
    def default_templates() -> list[WorkflowTemplate]:
        return [
            repository_audit_template(),
            secret_audit_template(),
            dependency_audit_template(),
            docker_compose_audit_template(),
            configuration_audit_template(),
            log_review_template(),
            hardening_plan_template(),
            incident_response_triage_template(),
        ]

    def register(self, template: WorkflowTemplate) -> None:
        if template.execution_allowed:
            raise ValueError("defensive workflows must not allow execution")
        self._templates[template.workflow_id] = template

    def get(self, workflow_id: str) -> WorkflowTemplate | None:
        return self._templates.get(workflow_id)

    def list_templates(self) -> list[WorkflowTemplate]:
        return list(self._templates.values())

    def build_plan(self, workflow_id: str, inputs: dict | None = None) -> WorkflowPlan | None:
        template = self.get(workflow_id)
        if template is None:
            return None
        return template.build_plan(inputs=inputs)
