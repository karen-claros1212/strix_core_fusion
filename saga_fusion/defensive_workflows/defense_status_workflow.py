from __future__ import annotations

from ._helpers import build_plan, classification


def run_defense_status_workflow(available_workflows: list[str] | None = None):
    workflows = list(available_workflows or [])
    return build_plan(
        "defense-status",
        "Defense Status Control Surface",
        "Summarize defensive lab/report-only availability without contacting Telegram, LLMs, tools, or external systems.",
        classification=classification("unknown", 0.0, "Defensive status summary only; no incident determination."),
        mitre_mappings=[],
        indicators=[],
        evidence={
            "available_workflow_count": len(workflows),
            "status_ref": "defensive-workflows:registry",
            "real_telegram_used": False,
            "real_llm_used": False,
            "real_tool_execution": False,
            "execution_allowed": False,
        },
        checklist=("Confirm lab mode", "Select a defensive workflow", "Attach only references or metadata"),
        recommendations=("Use explicit defensive workflow names", "Keep evidence reference-only", "Require reports for all defensive reviews"),
        memory_summary={"safe_to_store": True, "fields": ["workflow", "available_workflow_count"], "store_secrets": False},
        metadata={"available_workflows": workflows, "toolrouter_executes": False},
    )
