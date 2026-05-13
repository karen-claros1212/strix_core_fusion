import pytest

from saga_fusion.defensive_workflows import DefensiveWorkflowRegistry
from saga_fusion.task_planning import TaskPlanner


def test_registry_registers_all_workflows_and_blocks_unknown():
    registry = DefensiveWorkflowRegistry()
    ids = {definition.workflow_id for definition in registry.list_workflows()}
    assert {"malware_triage", "suspicious_process", "credential_theft", "ransomware_response", "webshell_investigation", "phishing_attachment"} <= ids
    for definition in registry.list_workflows():
        assert definition.execution_allowed is False
        assert definition.report_required is True
        assert definition.evidence_required is True
    assert registry.blocked_unknown("unknown") == {"workflow_id": "unknown", "blocked": True, "reason": "unknown_defensive_workflow", "execution_allowed": False}
    with pytest.raises(KeyError):
        registry.run("unknown")


def test_task_planner_references_advanced_defensive_workflow():
    plan = TaskPlanner().plan("please create a phishing attachment workflow", target="invoice.docm")
    assert plan.execution_allowed is False
    assert plan.metadata["workflow_plan"]["title"] == "Phishing Attachment Defensive Workflow"
    assert plan.metadata["workflow_plan"]["execution_allowed"] is False
