from __future__ import annotations

from pathlib import Path
from .workflow_types import WorkflowCategory, WorkflowPlan, WorkflowRisk, WorkflowTemplate, list_text_files, workflow_step

DEPENDENCY_FILES = ("requirements.txt", "pyproject.toml", "package.json", "package-lock.json", "poetry.lock", "Pipfile", "Gemfile", "go.mod", "Cargo.toml")


def dependency_audit_template() -> WorkflowTemplate:
    return WorkflowTemplate(
        workflow_id="dependency_audit",
        name="Dependency Defensive Audit",
        category=WorkflowCategory.DEPENDENCY_AUDIT,
        default_risk=WorkflowRisk.R3,
        allowed_mode="offline_inventory_only",
        required_inputs=("repo_path",),
        description="Plan dependency manifest inventory and offline vulnerability-review placeholder; no external calls by default.",
        tags=("dependencies", "offline", "dry_run"),
        steps=(
            workflow_step("package_files", "Package files", "Find dependency manifest and lock files.", ("package_files",)),
            workflow_step("inventory", "Inventory", "Build dependency inventory from available manifests.", ("dependency_inventory",)),
            workflow_step("vulnerability_review_placeholder", "Vulnerability review placeholder", "Mark external vulnerability checks as disabled unless explicitly approved later.", ("external_calls",)),
            workflow_step("risk_summary", "Risk summary", "Summarize unpinned/unknown dependency risks.", ("risk_summary",)),
        ),
        execution_allowed=False,
    )


def generate_dependency_audit_plan(repo_path: str | Path, **inputs) -> WorkflowPlan:
    root = Path(repo_path)
    files = [p for p in list_text_files(root) if p.name in DEPENDENCY_FILES]
    evidence = {
        "package_files": [str(p.relative_to(root)) for p in files],
        "external_calls": False,
        "vulnerability_review": "placeholder_disabled_by_default",
        "risk_summary": "offline_manifest_inventory_only",
        "execution_allowed": False,
    }
    return dependency_audit_template().build_plan(inputs={"repo_path": str(root), **inputs}, evidence=evidence, notes=("no_external_calls_by_default",))
