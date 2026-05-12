from __future__ import annotations

from .tool_scope_types import ToolScope


class ToolsetScopeRegistry:
    """Registry of clean-room STRIX toolset scopes; metadata only, no execution."""

    def __init__(self) -> None:
        self._toolsets: dict[str, ToolScope] = {}
        for scope in self._default_toolsets():
            self.register(scope)

    def register(self, scope: ToolScope) -> ToolScope:
        if not scope.name:
            raise ValueError("toolset name is required")
        if scope.name in self._toolsets:
            raise ValueError(f"duplicate toolset: {scope.name}")
        if not scope.allowed_tools:
            raise ValueError("toolset allowed_tools is required")
        overlap = set(scope.allowed_tools) & set(scope.denied_tools)
        if overlap:
            raise ValueError(f"toolset cannot both allow and deny: {sorted(overlap)}")
        self._toolsets[scope.name] = scope
        return scope

    def get(self, name: str) -> ToolScope | None:
        return self._toolsets.get(str(name or "").strip().lower())

    def list_toolsets(self) -> list[ToolScope]:
        return list(self._toolsets.values())

    def allowed_tools_for(self, names: str | list[str] | tuple[str, ...] | set[str]) -> set[str]:
        allowed: set[str] = set()
        for name in self._iter_names(names):
            scope = self.get(name)
            if scope is not None:
                allowed.update(scope.allowed_tools)
                allowed.difference_update(scope.denied_tools)
        return allowed

    def denied_tools_for(self, names: str | list[str] | tuple[str, ...] | set[str]) -> set[str]:
        denied: set[str] = set()
        for name in self._iter_names(names):
            scope = self.get(name)
            if scope is not None:
                denied.update(scope.denied_tools)
        return denied

    @staticmethod
    def _iter_names(names):
        if names is None:
            return ()
        if isinstance(names, str):
            return (names,)
        return tuple(names)

    @staticmethod
    def _default_toolsets() -> tuple[ToolScope, ...]:
        return (
            ToolScope("repo_audit", "repo_audit", ("repo_audit", "dependency_audit", "config_audit", "evidence_list", "report_generate"), ("cloudops_plan", "dns_plan", "firewall_plan", "backup_plan"), "Repository audit dry-run tools."),
            ToolScope("secret_audit", "secret_audit", ("secret_scan", "evidence_list", "report_generate"), ("cloudops_plan", "dns_plan", "firewall_plan", "backup_plan"), "Secret audit metadata tools."),
            ToolScope("docker_audit", "docker_audit", ("docker_audit", "config_audit", "evidence_list", "report_generate"), ("cloudops_plan", "dns_plan", "firewall_plan", "backup_plan"), "Docker and compose audit tools."),
            ToolScope("reporting", "reporting", ("report_generate", "evidence_list", "status"), ("cloudops_plan", "dns_plan", "firewall_plan", "backup_plan"), "Report and evidence read-only tools."),
            ToolScope("cloudops_plan", "cloudops_plan", ("cloudops_plan", "dns_plan", "firewall_plan", "backup_plan", "evidence_list", "report_generate"), (), "CloudOps planning only; R4 approval still applies."),
            ToolScope("llm_only", "llm_only", ("llm_analyze", "status", "evidence_list"), ("cloudops_plan", "dns_plan", "firewall_plan", "backup_plan"), "Reasoning-only LLM tools."),
        )


__all__ = ["ToolsetScopeRegistry"]
