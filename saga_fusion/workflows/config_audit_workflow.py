from __future__ import annotations

import re
from pathlib import Path
from .workflow_types import WorkflowCategory, WorkflowPlan, WorkflowRisk, WorkflowTemplate, list_text_files, read_small, workflow_step

CONFIG_NAMES = (".env.example", "config.json", "settings.py", "settings.toml", "appsettings.json", "docker-compose.yml", "docker-compose.yaml")
INSECURE_PATTERNS = {
    "debug_enabled": re.compile(r"(?i)\b(debug|dev_mode)\b\s*[:=]\s*(true|1|yes)"),
    "wildcard_host": re.compile(r"(?i)(allowed_hosts|cors|origin).*?(\*|0\.0\.0\.0)"),
    "tls_disabled": re.compile(r"(?i)(tls|ssl|verify).*?[:=]\s*(false|0|no)"),
    "default_password": re.compile(r"(?i)(password|secret).*?[:=]\s*(changeme|password|admin|default)"),
}


def configuration_audit_template() -> WorkflowTemplate:
    return WorkflowTemplate(
        workflow_id="configuration_audit",
        name="Configuration Defensive Audit",
        category=WorkflowCategory.CONFIGURATION_AUDIT,
        default_risk=WorkflowRisk.R3,
        allowed_mode="evidence_only",
        required_inputs=("repo_path",),
        description="Plan review of env examples, defaults, insecure defaults, missing env vars, and report.",
        tags=("config", "env", "insecure_defaults"),
        steps=(
            workflow_step("env_example", ".env.example", "Check sample environment files for safe placeholders.", ("env_examples",)),
            workflow_step("defaults", "Defaults", "Inventory configuration defaults.", ("config_files",)),
            workflow_step("insecure_defaults", "Insecure defaults", "Flag debug, wildcard, disabled TLS, and default-password patterns.", ("insecure_defaults",)),
            workflow_step("missing_env_vars", "Missing env vars", "Identify referenced env vars not represented in examples.", ("missing_env_vars",)),
            workflow_step("report", "Report", "Generate report-only configuration findings.", ("report_required",)),
        ),
        execution_allowed=False,
    )


def generate_config_audit_plan(repo_path: str | Path, **inputs) -> WorkflowPlan:
    root = Path(repo_path)
    files = [p for p in list_text_files(root) if p.name in CONFIG_NAMES]
    env_examples = [str(p.relative_to(root)) for p in files if p.name == ".env.example"]
    insecure = []
    referenced_envs = set()
    example_envs = set()
    for path in list_text_files(root):
        rel = str(path.relative_to(root))
        text = read_small(path)
        for env in re.findall(r"os\.environ\.get\(['\"]([A-Z0-9_]+)['\"]\)|getenv\(['\"]([A-Z0-9_]+)['\"]\)", text):
            referenced_envs.update(item for item in env if item)
        if path.name == ".env.example":
            for line in text.splitlines():
                if "=" in line and not line.strip().startswith("#"):
                    example_envs.add(line.split("=", 1)[0].strip())
        if path in files:
            for line_no, line in enumerate(text.splitlines(), 1):
                for rule, pattern in INSECURE_PATTERNS.items():
                    if pattern.search(line):
                        insecure.append({"file": rel, "line": line_no, "rule": rule, "snippet": line.strip()[:100]})
    evidence = {
        "env_examples": env_examples,
        "config_files": [str(p.relative_to(root)) for p in files],
        "insecure_defaults": insecure,
        "missing_env_vars": sorted(referenced_envs - example_envs),
        "execution_allowed": False,
    }
    return configuration_audit_template().build_plan(inputs={"repo_path": str(root), **inputs}, evidence=evidence, notes=("report_only",))
