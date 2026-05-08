from __future__ import annotations

import ast
import hashlib
import json
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Iterable

IGNORE_DIRS = {
    ".git", ".venv", "venv", "__pycache__", ".pytest_cache", "node_modules",
    "reports/quarantine", "reports/forensic_untracked",
}
TEXT_EXTENSIONS = {
    ".py", ".md", ".txt", ".toml", ".yaml", ".yml", ".json", ".ini", ".cfg",
    ".env", ".example", ".sh", ".Dockerfile", "", ".gitignore",
}
SECRET_PATTERNS = [
    ("github_token", re.compile(r"ghp_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]+")),
    ("telegram_token", re.compile(r"\b\d{6,}:[A-Za-z0-9_-]{20,}\b")),
    ("api_key_assignment", re.compile(r"(?i)(api[_-]?key|secret[_-]?key|password|token)\s*=\s*[^\s]+")),
    ("private_key", re.compile(r"BEGIN (RSA |EC |OPENSSH |)PRIVATE KEY")),
]
DOCKER_PATTERNS = [
    ("privileged", re.compile(r"privileged\s*:\s*true|--privileged", re.I)),
    ("docker_sock", re.compile(r"/var/run/docker\.sock", re.I)),
    ("host_network", re.compile(r"network_mode\s*:\s*host|--network\s+host", re.I)),
    ("latest_tag", re.compile(r"image\s*:\s*[^\s:]+:latest", re.I)),
]
CONFIG_PATTERNS = [
    ("bind_all_interfaces", re.compile(r"0\.0\.0\.0", re.I)),
    ("debug_enabled", re.compile(r"(?i)debug\s*=\s*true|DEBUG\s*=\s*1")),
    ("insecure_verify_disabled", re.compile(r"(?i)verify\s*=\s*false|ssl_verify\s*=\s*false")),
]


@dataclass
class Finding:
    category: str
    severity: str
    path: str
    line: int
    title: str
    evidence: str
    recommendation: str


@dataclass
class RepoAuditResult:
    repo_root: str
    generated_at_utc: str
    mode: str = "dry_run"
    file_count: int = 0
    python_file_count: int = 0
    docker_file_count: int = 0
    import_count: int = 0
    findings: list[Finding] = field(default_factory=list)
    dependency_imports: dict[str, int] = field(default_factory=dict)
    touched_production: bool = False

    def to_dict(self) -> dict:
        data = asdict(self)
        data["findings"] = [asdict(finding) for finding in self.findings]
        return data


class RepoAuditor:
    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()

    def audit(self) -> RepoAuditResult:
        result = RepoAuditResult(
            repo_root=str(self.root),
            generated_at_utc=datetime.utcnow().isoformat() + "Z",
        )
        imports: dict[str, int] = {}
        for path in self._iter_files():
            rel = self._rel(path)
            result.file_count += 1
            if path.suffix == ".py":
                result.python_file_count += 1
                self._collect_python_imports(path, imports)
            if self._is_docker_file(path):
                result.docker_file_count += 1
            if self._is_text_file(path):
                text = path.read_text(errors="ignore")
                self._scan_secrets(rel, text, result)
                self._scan_docker(rel, text, result)
                self._scan_config(rel, text, result)
        result.dependency_imports = dict(sorted(imports.items()))
        result.import_count = sum(imports.values())
        return result

    def write_evidence(self, result: RepoAuditResult, evidence_dir: str | Path) -> Path:
        out_dir = Path(evidence_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(result.to_dict(), indent=2, sort_keys=True)
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
        path = out_dir / f"repo_audit_6c1_{digest}.json"
        path.write_text(payload)
        return path

    def _iter_files(self) -> Iterable[Path]:
        for path in self.root.rglob("*"):
            if not path.is_file():
                continue
            rel_parts = path.relative_to(self.root).parts
            rel_join = "/".join(rel_parts)
            if any(part in IGNORE_DIRS for part in rel_parts):
                continue
            if any(rel_join.startswith(prefix + "/") for prefix in IGNORE_DIRS if "/" in prefix):
                continue
            yield path

    def _rel(self, path: Path) -> str:
        return str(path.relative_to(self.root))

    def _is_text_file(self, path: Path) -> bool:
        return path.suffix in TEXT_EXTENSIONS or path.name in {"Dockerfile", ".env.example", ".gitignore"}

    def _is_docker_file(self, path: Path) -> bool:
        name = path.name.lower()
        return name == "dockerfile" or "docker-compose" in name or name.endswith(".dockerfile")

    def _collect_python_imports(self, path: Path, imports: dict[str, int]) -> None:
        try:
            tree = ast.parse(path.read_text(errors="ignore"))
        except SyntaxError:
            return
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top = alias.name.split(".")[0]
                    imports[top] = imports.get(top, 0) + 1
            elif isinstance(node, ast.ImportFrom) and node.module:
                top = node.module.split(".")[0]
                imports[top] = imports.get(top, 0) + 1

    def _add(self, result: RepoAuditResult, category: str, severity: str, path: str, line: int, title: str, evidence: str, recommendation: str) -> None:
        result.findings.append(Finding(category, severity, path, line, title, self._redact(evidence), recommendation))

    def _scan_secrets(self, rel: str, text: str, result: RepoAuditResult) -> None:
        for idx, line in enumerate(text.splitlines(), start=1):
            if self._is_safe_env_example_placeholder(rel, line):
                continue
            for name, pattern in SECRET_PATTERNS:
                if pattern.search(line):
                    self._add(result, "secret_scan", "HIGH", rel, idx, f"Potential secret pattern: {name}", line.strip(), "Move secrets to runtime env and keep only placeholders in repo.")

    def _is_safe_env_example_placeholder(self, rel: str, line: str) -> bool:
        if not rel.endswith(".env.example") or "=" not in line or line.lstrip().startswith("#"):
            return False
        key, value = line.split("=", 1)
        normalized_key = key.strip().upper()
        normalized_value = value.strip().strip("\"'").lower()
        if not any(marker in normalized_key for marker in ("TOKEN", "API_KEY", "SECRET", "PASSWORD")):
            return False
        return normalized_value in {"", "local", "example", "changeme", "placeholder", "<redacted>", "<secret>"}

    def _scan_docker(self, rel: str, text: str, result: RepoAuditResult) -> None:
        if "docker" not in rel.lower() and "compose" not in rel.lower() and "Dockerfile" not in rel:
            return
        for idx, line in enumerate(text.splitlines(), start=1):
            for name, pattern in DOCKER_PATTERNS:
                if pattern.search(line):
                    self._add(result, "docker_audit", "MED", rel, idx, f"Docker risk: {name}", line.strip(), "Review container privilege, networking, mounts, and image pinning before production use.")

    def _scan_config(self, rel: str, text: str, result: RepoAuditResult) -> None:
        if rel.startswith("tests/"):
            return
        for idx, line in enumerate(text.splitlines(), start=1):
            for name, pattern in CONFIG_PATTERNS:
                if pattern.search(line):
                    self._add(result, "config_audit", "LOW", rel, idx, f"Config risk: {name}", line.strip(), "Confirm this setting is lab-only or restrict it for production.")

    def _redact(self, text: str) -> str:
        redacted = text
        redacted = re.sub(r"ghp_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+", "[REDACTED_GITHUB_TOKEN]", redacted)
        redacted = re.sub(r"\b\d{6,}:[A-Za-z0-9_-]{20,}\b", "[REDACTED_TELEGRAM_TOKEN]", redacted)
        redacted = re.sub(r"(?i)((api[_-]?key|secret[_-]?key|password|token)\s*=\s*)[^\s]+", r"\1[REDACTED]", redacted)
        return redacted
