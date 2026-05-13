from saga_fusion.cyber_knowledge import IncidentPlaybookRegistry


def test_required_playbooks_exist_and_are_non_executing():
    registry = IncidentPlaybookRegistry()
    required = {
        "malware_triage",
        "suspicious_process_review",
        "credential_theft_investigation",
        "ransomware_containment_plan",
        "webshell_investigation",
        "phishing_attachment_review",
    }
    found = {p.playbook_id for p in registry.list_playbooks()}
    assert required <= found
    for playbook_id in required:
        playbook = registry.get(playbook_id)
        assert playbook is not None
        assert playbook.execution_allowed is False
        assert playbook.steps
        assert playbook.evidence_to_collect


def test_task_planner_references_cyber_playbook_without_execution():
    from saga_fusion.task_planning import TaskPlanner

    plan = TaskPlanner().plan("please use the malware triage playbook for reported suspicious binary behavior")
    assert plan.execution_allowed is False
    assert plan.metadata["cyber_playbook"]["playbook_id"] == "malware_triage"
    assert plan.metadata["cyber_playbook"]["execution_allowed"] is False
