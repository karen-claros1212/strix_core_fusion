from __future__ import annotations

import re
from pathlib import Path
from .workflow_types import WorkflowCategory, WorkflowPlan, WorkflowRisk, WorkflowTemplate, list_text_files, read_small, workflow_step

DOCKER_NAMES = ("Dockerfile", "docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml")


def docker_compose_audit_template() -> WorkflowTemplate:
    return WorkflowTemplate(
        workflow_id="docker_compose_audit",
        name="Docker / Compose Defensive Audit",
        category=WorkflowCategory.DOCKER_AUDIT,
        default_risk=WorkflowRisk.R3,
        allowed_mode="evidence_only",
        required_inputs=("repo_path",),
        description="Plan Dockerfile/Compose review for privileges, exposed ports, volumes, env secrets, and recommendations.",
        tags=("docker", "compose", "containers"),
        steps=(
            workflow_step("dockerfile_compose_detection", "Dockerfile/Compose detection", "Find Docker and Compose files.", ("docker_files",)),
            workflow_step("privileged_container_risks", "Privileged/container risks", "Flag privileged mode, host network, and container escape risk indicators.", ("privileged_risks",)),
            workflow_step("exposed_ports", "Exposed ports", "Identify published or exposed ports for review.", ("exposed_ports",)),
            workflow_step("volume_mounts", "Volume mounts", "Identify host volume mounts needing least-privilege review.", ("volume_mounts",)),
            workflow_step("secrets_in_env", "Secrets in env", "Flag secret-like environment keys without printing values.", ("env_secret_keys",)),
            workflow_step("recommendations", "Recommendations", "Generate hardening recommendations only.", ("recommendations",)),
        ),
        execution_allowed=False,
    )


def generate_docker_audit_plan(repo_path: str | Path, **inputs) -> WorkflowPlan:
    root = Path(repo_path)
    docker_files = [p for p in list_text_files(root) if p.name in DOCKER_NAMES]
    privileged = []
    ports = []
    volumes = []
    env_secret_keys = []
    for path in docker_files:
        rel = str(path.relative_to(root))
        for line_no, line in enumerate(read_small(path).splitlines(), 1):
            lower = line.lower()
            if "privileged" in lower and "true" in lower or "network_mode: host" in lower or "--privileged" in lower:
                privileged.append({"file": rel, "line": line_no, "indicator": "privileged_or_host_access"})
            if re.search(r"(?i)\b(expose|ports?)\b", line) or re.search(r"['\"]?\d{2,5}:\d{2,5}", line):
                ports.append({"file": rel, "line": line_no, "snippet": line.strip()[:80]})
            if re.search(r"(?i)\bvolumes?\b", line) or re.search(r"\s-\s*/[^:]+:", line):
                volumes.append({"file": rel, "line": line_no, "snippet": line.strip()[:80]})
            if re.search(r"(?i)(token|secret|password|api[_-]?key)\s*[:=]", line):
                key = re.split(r"[:=]", line.strip(), 1)[0].strip(" -\"'")
                env_secret_keys.append({"file": rel, "line": line_no, "key": key, "value": "[REDACTED]"})
    evidence = {
        "docker_files": [str(p.relative_to(root)) for p in docker_files],
        "privileged_risks": privileged,
        "exposed_ports": ports,
        "volume_mounts": volumes,
        "env_secret_keys": env_secret_keys,
        "recommendations": ["Disable privileged/host access unless justified", "Restrict published ports", "Move secrets to managed secret storage"],
        "execution_allowed": False,
    }
    return docker_compose_audit_template().build_plan(inputs={"repo_path": str(root), **inputs}, evidence=evidence, notes=("recommendations_only",))
