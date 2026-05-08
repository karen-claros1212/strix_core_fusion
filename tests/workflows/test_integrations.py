import asyncio
import json

from saga_fusion.reporting import ReportBuilder, TelegramReportFormatter
from saga_fusion.task_planning import TaskPlanner, TaskPlanStatus
from saga_fusion.telegram.mission_operator import TelegramMissionOperator
from saga_fusion.telegram.mock_telegram_adapter import MockTelegramAdapter
from saga_fusion.telegram.telegram_config import TelegramConfig
from saga_fusion.workflows import generate_hardening_plan


def test_task_planner_selects_workflow_by_intention_and_never_executes():
    planner = TaskPlanner()
    plan = planner.plan("please run a secret audit workflow", target=".")
    intent = planner.build_execution_intent(plan)
    assert plan.pattern_id == "defensive_secret_audit"
    assert plan.status == TaskPlanStatus.PLANNED
    assert plan.metadata["workflow_plan"]["workflow_id"] == "secret_audit"
    assert plan.metadata["workflow_plan"]["execution_allowed"] is False
    assert intent.execution_allowed is False


def test_r4_r5_requests_still_do_not_execute():
    planner = TaskPlanner()
    r4 = planner.plan("Crea un VPS en Hostinger")
    r5 = planner.plan("Elimina el servidor y borra backups")
    assert r4.execution_allowed is False
    assert planner.build_execution_intent(r4).execution_allowed is False
    assert r5.blocked is True
    assert planner.build_execution_intent(r5).execution_allowed is False


def test_reporting_summarizes_workflow_plan_for_telegram():
    workflow_plan = generate_hardening_plan("local lab")
    report = ReportBuilder().build_workflow_plan_report(workflow_plan, audience="telegram_summary")
    formatted = TelegramReportFormatter().format(report, artifact_ref="workflow:hardening_plan")
    assert "Workflow Plan hardening_plan" in report.title
    assert "Artifact: workflow:hardening_plan" in formatted
    assert "execution_allowed" in str(report.metadata)
    assert "True" not in str(report.metadata.get("execution_allowed"))


def test_telegram_mock_receives_workflow_plan_evidence_only():
    config = TelegramConfig(mode="mock", allowed_user_ids=["diego_claros"])
    operator = TelegramMissionOperator(config, MockTelegramAdapter())
    response = json.loads(asyncio.run(operator.handle_message("123", "diego_claros", "secret audit workflow for this repo")))
    assert response["status"] == "workflow_plan"
    assert response["workflow_id"] == "secret_audit"
    assert response["execution_allowed"] is False
    assert response["executed"] is False
    assert any(record["event_type"] == "task_plan_intent" for record in operator.evidence_logger.records)
