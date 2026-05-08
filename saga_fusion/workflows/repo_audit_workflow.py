from __future__ import annotations

from pathlib import Path
from .workflow_types import WorkflowCategory, WorkflowPlan, WorkflowRisk, WorkflowTemplate, list_text_files, workflow_step


def repository_audit_template() -> WorkflowTemplate:
    return WorkflowTemplate(
        workflow_id="repository_audit",
        name="Repository Defensive Audit",
        category=WorkflowCategory.REPOSITORY_AUDIT,
        default_risk=WorkflowRisk.R3,
        allowed_mode="evidence_only",
        required_inputs=("repo_path",),
        description="Plan a repository audit with inventory, secret/dependency/config review, and report.",
        tags=("repo", "dry_run", "evidence"),
        steps=(
            workflow_step("scope_validation", "Scope validation", "Validate authorized local repository scope before any review.", ("repo_path",)),
            workflow_step("file_inventory", "File inventory", "Inventory files and languages without modifying content.", ("file_count", "extensions")),
            workflow_step("secret_scan", "Secret scan", "Search for secret-like patterns with redaction.", ("secret_findings",)),
            workflow_step("dependency_scan", "Dependency scan", "Identify dependency manifest files for offline review.", ("dependency_files",)),
            workflow_step("config_scan", "Configuration scan", "Review safe config files for insecure defaults.", ("config_files",)),
            workflow_step("report", "Report", "Generate evidence-backed report and residual risk notes.", ("report_required",)),
        ),
        execution_allowed=False,
    )


def generate_repo_audit_plan(repo_path: str | Path, **inputs) -> WorkflowPlan:
    root = Path(repo_path)
    files = list_text_files(root)
    extensions: dict[str, int] = {}
    for path in files:
        ext = path.suffix or "[no_extension]"
        extensions[ext] = extensions.get(ext, 0) + 1
    dependency_names = {"requirements.txt", "pyproject.toml", "package.json", "package-lock.json", "Pipfile", "poetry.lock"}
    config_names = {".env.example", "config.json", "settings.py", "docker-compose.yml", "docker-compose.yaml"}
    evidence = {
        "repo_path": str(root),
        "file_count": len(files),
        "extensions": extensions,
        "dependency_files": [str(p.relative_to(root)) for p in files if p.name in dependency_names],
        "config_files": [str(p.relative_to(root)) for p in files if p.name in config_names],
        "execution_allowed": False,
    }
    payload = {"repo_path": str(root), **inputs}
    return repository_audit_template().build_plan(inputs=payload, evidence=evidence, notes=("plan_only", "no_auto_remediation"))
