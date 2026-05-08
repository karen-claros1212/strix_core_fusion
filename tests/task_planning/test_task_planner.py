from saga_fusion.task_planning import TaskPlanner, TaskPlanStatus, TaskRisk


def test_planner_builds_repo_audit_dry_run_plan_and_intent():
    planner = TaskPlanner()
    plan = planner.plan("run repo audit dry-run", target="/repo")
    intent = planner.build_execution_intent(plan)
    assert plan.pattern_id == "repo_audit_dry_run"
    assert plan.status == TaskPlanStatus.PLANNED
    assert plan.risk_level == TaskRisk.R3
    assert plan.execution_allowed is False
    assert intent.execution_allowed is False
    assert intent.dry_run is True
    assert intent.evidence_required is True
    assert planner.executed is False


def test_planner_builds_r4_approval_intent_for_cloud_create():
    planner = TaskPlanner()
    plan = planner.plan("Crea un VPS en Hostinger")
    intent = planner.build_execution_intent(plan)
    assert plan.pattern_id == "cloud_create_approval"
    assert plan.status == TaskPlanStatus.APPROVAL_REQUIRED
    assert plan.approval_required is True
    assert plan.blocked is False
    assert intent.approval_required is True
    assert intent.execution_allowed is False
    assert any(step.step_id == "approval_intent" for step in plan.steps)


def test_planner_builds_r5_blocked_intent_for_destructive_action():
    planner = TaskPlanner()
    plan = planner.plan("Elimina el servidor y borra backups")
    intent = planner.build_execution_intent(plan)
    assert plan.pattern_id == "destructive_block"
    assert plan.status == TaskPlanStatus.BLOCKED
    assert plan.blocked is True
    assert plan.approval_required is False
    assert intent.blocked is True
    assert intent.sandbox_mode == "blocked"
    assert intent.execution_allowed is False
    assert any(step.step_id == "blocked_intent" for step in plan.steps)


def test_unknown_pattern_requires_policy_review_and_never_allows_execution():
    planner = TaskPlanner()
    plan = planner.plan("invent a brand new unregistered operation")
    intent = planner.build_execution_intent(plan)
    assert plan.pattern_id == "unknown_pattern"
    assert plan.status == TaskPlanStatus.POLICY_REVIEW_REQUIRED
    assert plan.blocked is True
    assert plan.execution_allowed is False
    assert intent.execution_allowed is False
    assert "unknown_pattern" in intent.metadata["pattern_id"]


def test_plan_contains_reporting_ready_metadata():
    planner = TaskPlanner()
    plan = planner.plan("generate report from evidence")
    assert plan.metadata["reporting_ready"] is True
    assert "artifact_ref" in plan.metadata["reporting_tags"]
    assert plan.to_dict()["metadata"]["clean_room"] is True
