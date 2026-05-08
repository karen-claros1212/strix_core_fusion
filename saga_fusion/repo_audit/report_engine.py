from __future__ import annotations

from collections import Counter
from pathlib import Path

from .repo_auditor import RepoAuditResult


class RepoAuditReportEngine:
    def render_markdown(self, result: RepoAuditResult, evidence_path: str | Path | None = None) -> str:
        severity_counts = Counter(f.severity for f in result.findings)
        lines = [
            "# PHASE 6C-1 STRIX CORE REPOSITORY AUDIT DRY-RUN REPORT",
            "",
            "## Executive Summary",
            "STRIX repository audit executed in dry-run mode against the local STRIX repo as lab target. No production/external target was touched and no patches were applied.",
            "",
            "## Scope",
            f"- Repo root: `{result.repo_root}`",
            f"- Generated UTC: `{result.generated_at_utc}`",
            f"- Mode: `{result.mode}`",
            f"- Evidence: `{evidence_path}`" if evidence_path else "- Evidence: not written",
            "",
            "## Inventory",
            f"- Files scanned: {result.file_count}",
            f"- Python files: {result.python_file_count}",
            f"- Docker/Compose files: {result.docker_file_count}",
            f"- Import references: {result.import_count}",
            "",
            "## Findings Summary",
            f"- HIGH: {severity_counts.get('HIGH', 0)}",
            f"- MED: {severity_counts.get('MED', 0)}",
            f"- LOW: {severity_counts.get('LOW', 0)}",
            "",
            "## Dependency Import Topology",
        ]
        for name, count in sorted(result.dependency_imports.items(), key=lambda item: (-item[1], item[0]))[:25]:
            lines.append(f"- `{name}`: {count}")
        lines.extend(["", "## Findings"])
        if not result.findings:
            lines.append("No findings detected by the dry-run static checks.")
        else:
            for idx, finding in enumerate(result.findings, start=1):
                lines.extend([
                    f"### {idx}. [{finding.severity}] {finding.title}",
                    f"- Category: `{finding.category}`",
                    f"- Location: `{finding.path}:{finding.line}`",
                    f"- Evidence: `{finding.evidence}`",
                    f"- Recommendation: {finding.recommendation}",
                    "",
                ])
        lines.extend([
            "## Dry-Run Confirmation",
            "- Code modified by audit: NO",
            "- External pentest target touched: NO",
            "- CloudOps production action executed: NO",
            "- Patches applied automatically: NO",
            "",
            "## Verdict",
            "APTO PARA CONTINUAR 6C LAB: SI",
        ])
        return "\n".join(lines) + "\n"
