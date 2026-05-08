from __future__ import annotations

from .task_types import PatternDefinition, TaskCategory, TaskRisk


class PatternRegistry:
    """Deterministic clean-room registry of Saga Fusion planning patterns.

    The registry stores declarative patterns only. It does not import CAI code,
    create a CAI runtime, execute tools, or dispatch shell/browser/network work.
    """

    def __init__(self, patterns: list[PatternDefinition] | None = None):
        self._patterns: dict[str, PatternDefinition] = {}
        for pattern in patterns or self.default_patterns():
            self.register(pattern)

    @staticmethod
    def default_patterns() -> list[PatternDefinition]:
        return [
            PatternDefinition(
                pattern_id="status_check",
                name="Status / Health Check",
                category=TaskCategory.READ_ONLY,
                action_type="status",
                tool_name="status",
                risk_level=TaskRisk.R0,
                keywords=("status", "estado", "health", "salud", "list", "show"),
                description="Read-only system status or inventory request.",
                requires_sandbox=False,
                reporting_tags=("read_only", "telegram_safe"),
                safe_modes=("report_only",),
            ),
            PatternDefinition(
                pattern_id="repo_audit_dry_run",
                name="Repository Audit Dry-Run",
                category=TaskCategory.REPO_AUDIT,
                action_type="scan",
                tool_name="repo_audit",
                risk_level=TaskRisk.R3,
                keywords=("repo audit", "repository audit", "audita repo", "auditar repo", "scan repo", "dry-run", "dry run"),
                description="Internal repository audit plan with evidence/report output only.",
                reporting_tags=("evidence", "findings", "dry_run"),
            ),
            PatternDefinition(
                pattern_id="report_generation",
                name="Evidence Report Generation",
                category=TaskCategory.REPORTING,
                action_type="report",
                tool_name="reporting",
                risk_level=TaskRisk.R2,
                keywords=("report", "informe", "summary", "resumen", "evidence", "evidencia"),
                description="Build redacted reports from already captured evidence.",
                requires_sandbox=False,
                reporting_tags=("redaction", "artifact_ref", "telegram_summary"),
                safe_modes=("report_only",),
            ),
            PatternDefinition(
                pattern_id="cloud_create_approval",
                name="Cloud/Infrastructure Change Request",
                category=TaskCategory.CLOUDOPS,
                action_type="create",
                tool_name="cloudops",
                risk_level=TaskRisk.R4,
                keywords=("create vps", "crear vps", "crea un vps", "crea vps", "deploy", "desplegar", "open port", "abrir puerto", "change dns", "cambiar dns"),
                description="Infrastructure-changing request; plan only, explicit R4 approval required.",
                requires_approval=True,
                reporting_tags=("approval", "rollback_required", "sandbox_required"),
            ),
            PatternDefinition(
                pattern_id="destructive_block",
                name="Destructive / Exfiltration Block",
                category=TaskCategory.FILESYSTEM,
                action_type="delete",
                tool_name="blocked",
                risk_level=TaskRisk.R5,
                keywords=("delete", "destroy", "rm -rf", "elimina", "borra", "wipe", "exfiltrate", "filtra", "steal", "roba"),
                description="Destructive, exfiltration, or bypass request; non-approvable R5 block.",
                blocked=True,
                requires_approval=False,
                reporting_tags=("blocked", "r5", "non_approvable"),
                safe_modes=("blocked",),
            ),
        ]

    def register(self, pattern: PatternDefinition) -> None:
        if not pattern.pattern_id:
            raise ValueError("pattern_id is required")
        self._patterns[pattern.pattern_id] = pattern

    def get(self, pattern_id: str) -> PatternDefinition | None:
        return self._patterns.get(pattern_id)

    def list_patterns(self) -> list[PatternDefinition]:
        return list(self._patterns.values())

    def match(self, text: str) -> PatternDefinition | None:
        normalized = " ".join((text or "").lower().split())
        if not normalized:
            return None
        matches: list[tuple[int, int, PatternDefinition]] = []
        risk_order = {"R0": 0, "R1": 1, "R2": 2, "R3": 3, "R4": 4, "R5": 5}
        for pattern in self._patterns.values():
            matched_keywords = [kw for kw in pattern.keywords if kw and kw.lower() in normalized]
            if matched_keywords:
                longest = max(len(kw) for kw in matched_keywords)
                matches.append((risk_order[pattern.risk_level.value], longest, pattern))
        if not matches:
            return None
        # Highest risk wins first; then most specific keyword.
        return sorted(matches, key=lambda item: (item[0], item[1]), reverse=True)[0][2]
