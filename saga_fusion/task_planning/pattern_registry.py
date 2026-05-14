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
                keywords=("status", "estado", "health", "salud", "list", "show", "que puedes hacer", "qué puedes hacer", "capabilities", "ayuda"),
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
                pattern_id="defensive_repository_audit",
                name="Defensive Repository Audit Workflow",
                category=TaskCategory.DEFENSIVE_WORKFLOW,
                action_type="workflow",
                tool_name="defensive_workflow:repository_audit",
                risk_level=TaskRisk.R3,
                keywords=("repository audit workflow", "defensive repository audit", "repo audit workflow", "audit repository", "auditar repositorio"),
                description="Generate a repository defensive audit workflow plan only.",
                reporting_tags=("workflow", "repository_audit", "evidence_only"),
                safe_modes=("evidence_only", "report_only"),
            ),
            PatternDefinition(
                pattern_id="defensive_secret_audit",
                name="Defensive Secret Audit Workflow",
                category=TaskCategory.DEFENSIVE_WORKFLOW,
                action_type="workflow",
                tool_name="defensive_workflow:secret_audit",
                risk_level=TaskRisk.R3,
                keywords=("secret audit", "secrets audit", "scan secrets", "secret workflow", "audit secrets"),
                description="Generate a redacted secret-audit workflow plan only.",
                reporting_tags=("workflow", "secret_audit", "redacted"),
                safe_modes=("evidence_only", "report_only"),
            ),
            PatternDefinition(
                pattern_id="defensive_dependency_audit",
                name="Defensive Dependency Audit Workflow",
                category=TaskCategory.DEFENSIVE_WORKFLOW,
                action_type="workflow",
                tool_name="defensive_workflow:dependency_audit",
                risk_level=TaskRisk.R3,
                keywords=("dependency audit", "dependencies audit", "package audit", "audit dependencies"),
                description="Generate an offline dependency-audit workflow plan only.",
                reporting_tags=("workflow", "dependency_audit", "offline"),
                safe_modes=("evidence_only", "report_only"),
            ),
            PatternDefinition(
                pattern_id="defensive_docker_audit",
                name="Defensive Docker Audit Workflow",
                category=TaskCategory.DEFENSIVE_WORKFLOW,
                action_type="workflow",
                tool_name="defensive_workflow:docker_compose_audit",
                risk_level=TaskRisk.R3,
                keywords=("docker audit", "compose audit", "docker compose audit", "container audit"),
                description="Generate a Docker/Compose defensive-audit workflow plan only.",
                reporting_tags=("workflow", "docker_audit", "containers"),
                safe_modes=("evidence_only", "report_only"),
            ),
            PatternDefinition(
                pattern_id="defensive_configuration_audit",
                name="Defensive Configuration Audit Workflow",
                category=TaskCategory.DEFENSIVE_WORKFLOW,
                action_type="workflow",
                tool_name="defensive_workflow:configuration_audit",
                risk_level=TaskRisk.R3,
                keywords=("configuration audit", "config audit", "insecure defaults", "audit config"),
                description="Generate a configuration-audit workflow plan only.",
                reporting_tags=("workflow", "configuration_audit", "insecure_defaults"),
                safe_modes=("evidence_only", "report_only"),
            ),
            PatternDefinition(
                pattern_id="defensive_log_review",
                name="Defensive Log Review Workflow",
                category=TaskCategory.DEFENSIVE_WORKFLOW,
                action_type="workflow",
                tool_name="defensive_workflow:log_review",
                risk_level=TaskRisk.R2,
                keywords=("log review", "review logs", "log audit", "redact logs"),
                description="Generate a redacted log-review workflow plan only.",
                reporting_tags=("workflow", "log_review", "redacted"),
                safe_modes=("evidence_only", "report_only"),
            ),
            PatternDefinition(
                pattern_id="defensive_hardening_plan",
                name="Defensive Hardening Plan Workflow",
                category=TaskCategory.DEFENSIVE_WORKFLOW,
                action_type="workflow",
                tool_name="defensive_workflow:hardening_plan",
                risk_level=TaskRisk.R3,
                keywords=("hardening plan", "security hardening", "harden system", "plan hardening"),
                description="Generate a hardening plan only; no remediation execution.",
                reporting_tags=("workflow", "hardening_plan", "rollback"),
                safe_modes=("plan_only", "report_only"),
            ),
            PatternDefinition(
                pattern_id="defensive_incident_response",
                name="Incident Response Triage Workflow",
                category=TaskCategory.DEFENSIVE_WORKFLOW,
                action_type="workflow",
                tool_name="defensive_workflow:incident_response_triage",
                risk_level=TaskRisk.R4,
                keywords=("incident response", "incident triage", "ir triage", "containment plan", "breach triage"),
                description="Generate an incident-response triage plan; no real containment.",
                requires_approval=False,
                reporting_tags=("workflow", "incident_response", "plan_only"),
                safe_modes=("plan_only", "report_only"),
            ),

            PatternDefinition(
                pattern_id="phase10b_malware_triage_workflow",
                name="Advanced Malware Triage Workflow",
                category=TaskCategory.DEFENSIVE_WORKFLOW,
                action_type="workflow",
                tool_name="defensive_workflow:malware_triage",
                risk_level=TaskRisk.R3,
                keywords=("advanced malware triage", "malware triage workflow", "triage malware sample", "malware defensive workflow"),
                description="Generate malware triage classification, ATT&CK mapping, detections, evidence, and report only.",
                reporting_tags=("defensive_workflow", "malware_triage", "cyber_knowledge"),
                safe_modes=("plan_only", "report_only"),
            ),
            PatternDefinition(
                pattern_id="phase10b_suspicious_process_workflow",
                name="Suspicious Process Workflow",
                category=TaskCategory.DEFENSIVE_WORKFLOW,
                action_type="workflow",
                tool_name="defensive_workflow:suspicious_process",
                risk_level=TaskRisk.R3,
                keywords=("suspicious process workflow", "review suspicious process", "process defensive workflow", "procesos raros", "proceso raro", "procesos sospechosos", "revisar procesos raros", "quiero revisar procesos raros"),
                description="Generate suspicious-process review checklist and read-only command suggestions only.",
                reporting_tags=("defensive_workflow", "suspicious_process", "read_only"),
                safe_modes=("plan_only", "report_only"),
            ),
            PatternDefinition(
                pattern_id="phase10b_credential_theft_workflow",
                name="Credential Theft Workflow",
                category=TaskCategory.DEFENSIVE_WORKFLOW,
                action_type="workflow",
                tool_name="defensive_workflow:credential_theft",
                risk_level=TaskRisk.R3,
                keywords=("credential theft workflow", "stealer defensive workflow", "credential theft defensive", "credential theft investigation workflow"),
                description="Generate stealer indicators, evidence paths, and containment recommendations without secret exposure.",
                reporting_tags=("defensive_workflow", "credential_theft", "redacted"),
                safe_modes=("plan_only", "report_only"),
            ),
            PatternDefinition(
                pattern_id="phase10b_ransomware_response_workflow",
                name="Ransomware Response Workflow",
                category=TaskCategory.DEFENSIVE_WORKFLOW,
                action_type="workflow",
                tool_name="defensive_workflow:ransomware_response",
                risk_level=TaskRisk.R4,
                keywords=("ransomware response workflow", "ransomware defensive workflow", "ransomware response plan"),
                description="Generate ransomware triage, isolation recommendation, evidence preservation, and backup review plan only.",
                requires_approval=False,
                reporting_tags=("defensive_workflow", "ransomware", "plan_only"),
                safe_modes=("plan_only", "report_only"),
            ),
            PatternDefinition(
                pattern_id="phase10b_webshell_investigation_workflow",
                name="Webshell Investigation Workflow",
                category=TaskCategory.DEFENSIVE_WORKFLOW,
                action_type="workflow",
                tool_name="defensive_workflow:webshell_investigation",
                risk_level=TaskRisk.R3,
                keywords=("webshell investigation workflow", "web shell investigation", "webshell defensive workflow"),
                description="Generate webshell investigation indicators, logs, and defensive detections only.",
                reporting_tags=("defensive_workflow", "webshell", "detection_engineering"),
                safe_modes=("plan_only", "report_only"),
            ),
            PatternDefinition(
                pattern_id="phase10b_phishing_attachment_workflow",
                name="Phishing Attachment Workflow",
                category=TaskCategory.DEFENSIVE_WORKFLOW,
                action_type="workflow",
                tool_name="defensive_workflow:phishing_attachment",
                risk_level=TaskRisk.R3,
                keywords=("phishing attachment workflow", "phishing attachment defensive", "review phishing attachment", "phishing", "parece phishing", "analiza si esto parece phishing", "adjunto sospechoso", "correo sospechoso"),
                description="Generate conceptual static-analysis plan and defensive rules without attachment execution.",
                reporting_tags=("defensive_workflow", "phishing_attachment", "no_execution"),
                safe_modes=("plan_only", "report_only"),
            ),
            PatternDefinition(
                pattern_id="cyber_malware_triage_playbook",
                name="Cyber Malware Triage Playbook",
                category=TaskCategory.DEFENSIVE_WORKFLOW,
                action_type="playbook",
                tool_name="cyber_playbook:malware_triage",
                risk_level=TaskRisk.R3,
                keywords=("malware triage", "malware playbook", "classify malware", "malware taxonomy"),
                description="Reference the non-executing malware triage playbook and cyber knowledge taxonomy.",
                reporting_tags=("cyber_knowledge", "malware_triage", "playbook_only"),
                safe_modes=("plan_only", "report_only"),
            ),
            PatternDefinition(
                pattern_id="cyber_ransomware_containment_playbook",
                name="Cyber Ransomware Containment Playbook",
                category=TaskCategory.DEFENSIVE_WORKFLOW,
                action_type="playbook",
                tool_name="cyber_playbook:ransomware_containment_plan",
                risk_level=TaskRisk.R4,
                keywords=("ransomware containment", "ransomware plan", "ransomware playbook"),
                description="Reference the non-executing ransomware containment planning playbook; real containment remains approval-gated.",
                requires_approval=False,
                reporting_tags=("cyber_knowledge", "ransomware", "containment_plan_only"),
                safe_modes=("plan_only", "report_only"),
            ),
            PatternDefinition(
                pattern_id="cyber_credential_theft_playbook",
                name="Cyber Credential Theft Investigation Playbook",
                category=TaskCategory.DEFENSIVE_WORKFLOW,
                action_type="playbook",
                tool_name="cyber_playbook:credential_theft_investigation",
                risk_level=TaskRisk.R3,
                keywords=("credential theft investigation", "credential theft playbook", "stealer investigation"),
                description="Reference the non-executing credential theft investigation playbook.",
                reporting_tags=("cyber_knowledge", "credential_theft", "playbook_only"),
                safe_modes=("plan_only", "report_only"),
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

    def attach_skill_metadata(self, pattern_id: str, skill_metadata: dict) -> PatternDefinition:
        """Attach declarative skill metadata to a planning pattern; no execution binding."""
        pattern = self.get(pattern_id)
        if pattern is None:
            raise KeyError(f"unknown pattern: {pattern_id}")
        updated = PatternDefinition(**{**pattern.__dict__, "skill_metadata": dict(skill_metadata or {})})
        self._patterns[pattern_id] = updated
        return updated

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
