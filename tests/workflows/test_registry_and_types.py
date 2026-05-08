from saga_fusion.workflows import DefensiveWorkflowRegistry, WorkflowPlan


def test_registry_registers_8_templates_all_execution_disallowed():
    registry = DefensiveWorkflowRegistry()
    templates = registry.list_templates()
    ids = {template.workflow_id for template in templates}
    assert ids == {
        "repository_audit",
        "secret_audit",
        "dependency_audit",
        "docker_compose_audit",
        "configuration_audit",
        "log_review",
        "hardening_plan",
        "incident_response_triage",
    }
    assert len(templates) == 8
    assert all(template.execution_allowed is False for template in templates)
    assert all(step.execution_allowed is False for template in templates for step in template.steps)


def test_unknown_workflow_does_not_execute():
    registry = DefensiveWorkflowRegistry()
    assert registry.get("unknown") is None
    assert registry.build_plan("unknown", {"repo_path": "."}) is None


def test_each_template_generates_workflow_plan_with_steps_evidence_report():
    registry = DefensiveWorkflowRegistry()
    input_by_id = {
        "repository_audit": {"repo_path": "."},
        "secret_audit": {"repo_path": "."},
        "dependency_audit": {"repo_path": "."},
        "docker_compose_audit": {"repo_path": "."},
        "configuration_audit": {"repo_path": "."},
        "log_review": {"log_path": "."},
        "hardening_plan": {"scope": "test scope"},
        "incident_response_triage": {"incident_summary": "test incident"},
    }
    for template in registry.list_templates():
        plan = template.build_plan(inputs=input_by_id[template.workflow_id])
        assert isinstance(plan, WorkflowPlan)
        assert plan.workflow_id == template.workflow_id
        assert plan.steps
        assert plan.evidence_required is True
        assert plan.report_required is True
        assert plan.execution_allowed is False
        assert plan.to_dict()["execution_allowed"] is False
