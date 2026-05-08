from __future__ import annotations

from .tool_routing_types import ToolCategory, ToolMetadata, ToolRisk


class ToolRegistry:
    def __init__(self):
        self._tools = {
            'status': ToolMetadata('status', ToolCategory.READ_ONLY, ToolRisk.R0, False, False, ('mock','real','dry_run'), 'Read system status.'),
            'repo_audit': ToolMetadata('repo_audit', ToolCategory.REPO_AUDIT, ToolRisk.R3, True, False, ('mock','real','dry_run'), 'Dry-run repository audit.'),
            'secret_scan': ToolMetadata('secret_scan', ToolCategory.REPO_AUDIT, ToolRisk.R2, True, False, ('mock','real','dry_run'), 'Dry-run secret scan.'),
            'dependency_audit': ToolMetadata('dependency_audit', ToolCategory.REPO_AUDIT, ToolRisk.R2, True, False, ('mock','real','dry_run'), 'Dependency audit.'),
            'config_audit': ToolMetadata('config_audit', ToolCategory.REPO_AUDIT, ToolRisk.R2, True, False, ('mock','real','dry_run'), 'Configuration audit.'),
            'docker_audit': ToolMetadata('docker_audit', ToolCategory.REPO_AUDIT, ToolRisk.R2, True, False, ('mock','real','dry_run'), 'Docker/Compose audit.'),
            'report_generate': ToolMetadata('report_generate', ToolCategory.REPORTING, ToolRisk.R1, False, False, ('mock','real','dry_run'), 'Generate redacted report.'),
            'cloudops_plan': ToolMetadata('cloudops_plan', ToolCategory.CLOUDOPS, ToolRisk.R4, True, True, ('mock','real','dry_run'), 'Plan CloudOps action; no execution by default.'),
            'dns_plan': ToolMetadata('dns_plan', ToolCategory.CLOUDOPS, ToolRisk.R4, True, True, ('mock','real','dry_run'), 'Plan DNS change; no execution by default.'),
            'firewall_plan': ToolMetadata('firewall_plan', ToolCategory.CLOUDOPS, ToolRisk.R4, True, True, ('mock','real','dry_run'), 'Plan firewall change; no execution by default.'),
            'backup_plan': ToolMetadata('backup_plan', ToolCategory.CLOUDOPS, ToolRisk.R4, True, True, ('mock','real','dry_run'), 'Plan backup/restore action; no execution by default.'),
            'llm_analyze': ToolMetadata('llm_analyze', ToolCategory.LLM_ONLY, ToolRisk.R1, False, False, ('mock','real','dry_run'), 'Reasoning-only LLM analysis.'),
            'evidence_list': ToolMetadata('evidence_list', ToolCategory.READ_ONLY, ToolRisk.R1, False, False, ('mock','real','dry_run'), 'List evidence metadata.'),
        }

    def get(self, name: str) -> ToolMetadata | None:
        return self._tools.get((name or '').strip().lower())

    def exists(self, name: str) -> bool:
        return self.get(name) is not None

    def list_tools(self) -> list[ToolMetadata]:
        return list(self._tools.values())
