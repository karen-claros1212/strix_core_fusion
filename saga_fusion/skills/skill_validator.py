from __future__ import annotations

import re
from typing import Iterable

from ..tool_routing import ToolRegistry
from .skill_manifest import SkillManifest

_DANGEROUS_PERMISSIONS = {
    "execute",
    "shell",
    "subprocess",
    "network_raw",
    "cloudops_execute",
    "telegram_real",
    "external_pentest",
    "secret_read",
    "read_secret",
    "env_read",
    "env_dump",
    "bypass_policy",
    "bypass_mission_policy",
    "bypass_sandbox",
    "disable_sandbox",
    "approval_bypass",
}
_ENTRYPOINT_RE = re.compile(r"^[a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*)*:[a-zA-Z_]\w*$")
_ENV_NAME_RE = re.compile(r"^[A-Z_][A-Z0-9_]*$")
_ALLOWED_PERMISSION_RE = re.compile(r"^[a-z][a-z0-9_:-]*$")


class SkillValidator:
    """Validates declarative skill metadata without loading modules or secrets."""

    def __init__(self, tool_registry: ToolRegistry | None = None, dangerous_permissions: Iterable[str] | None = None):
        self.tool_registry = tool_registry or ToolRegistry()
        self.dangerous_permissions = set(dangerous_permissions or _DANGEROUS_PERMISSIONS)

    def validate(self, manifest: SkillManifest) -> None:
        if not isinstance(manifest, SkillManifest):
            raise ValueError("manifest must be SkillManifest")
        self._required_fields(manifest)
        self._permissions(manifest)
        self._tool_scope(manifest)
        self._env_requirements(manifest)
        self._entrypoint(manifest)

    def is_valid(self, manifest: SkillManifest) -> bool:
        try:
            self.validate(manifest)
            return True
        except ValueError:
            return False

    def _required_fields(self, manifest: SkillManifest) -> None:
        required = {
            "name": manifest.name,
            "version": manifest.version,
            "description": manifest.description,
            "category": manifest.category,
            "risk_level": manifest.risk_level.value,
            "entrypoint": manifest.entrypoint,
        }
        missing = [field for field, value in required.items() if not value]
        if missing:
            raise ValueError(f"missing required fields: {', '.join(missing)}")
        if not manifest.permissions:
            raise ValueError("permissions must not be empty")
        if not manifest.allowed_tools:
            raise ValueError("allowed_tools must not be empty")

    def _permissions(self, manifest: SkillManifest) -> None:
        for permission in manifest.permissions:
            normalized = permission.strip().lower()
            if not _ALLOWED_PERMISSION_RE.match(normalized):
                raise ValueError(f"invalid permission format: {permission}")
            if normalized in self.dangerous_permissions or "secret" in normalized or "bypass" in normalized:
                raise ValueError(f"dangerous permission rejected: {permission}")

    def _tool_scope(self, manifest: SkillManifest) -> None:
        for tool_name in manifest.allowed_tools:
            if not self.tool_registry.exists(tool_name):
                raise ValueError(f"unknown allowed tool: {tool_name}")

    def _env_requirements(self, manifest: SkillManifest) -> None:
        for env_name in manifest.required_env:
            if "=" in env_name or env_name.startswith("$"):
                raise ValueError("required_env must contain variable names only, not values")
            if not _ENV_NAME_RE.match(env_name):
                raise ValueError(f"invalid env variable name: {env_name}")

    def _entrypoint(self, manifest: SkillManifest) -> None:
        if not _ENTRYPOINT_RE.match(manifest.entrypoint):
            raise ValueError("entrypoint must use module.path:function format")


__all__ = ["SkillValidator"]
