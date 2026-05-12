from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any

from .skill_types import SkillRiskLevel


def _tuple_of_strings(values: Any, field_name: str) -> tuple[str, ...]:
    if values is None:
        return ()
    if isinstance(values, str) or not isinstance(values, (list, tuple, set)):
        raise ValueError(f"{field_name} must be a list/tuple/set of strings")
    normalized: list[str] = []
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field_name} entries must be non-empty strings")
        normalized.append(value.strip())
    return tuple(normalized)


@dataclass(frozen=True)
class SkillManifest:
    """Declarative skill/plugin metadata only; never an execution object."""

    name: str
    version: str
    description: str
    category: str
    permissions: tuple[str, ...]
    allowed_tools: tuple[str, ...]
    required_env: tuple[str, ...]
    risk_level: SkillRiskLevel
    entrypoint: str
    enabled: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", str(self.name or "").strip().lower())
        object.__setattr__(self, "version", str(self.version or "").strip())
        object.__setattr__(self, "description", str(self.description or "").strip())
        object.__setattr__(self, "category", str(self.category or "").strip().lower())
        object.__setattr__(self, "permissions", _tuple_of_strings(self.permissions, "permissions"))
        object.__setattr__(self, "allowed_tools", tuple(tool.lower() for tool in _tuple_of_strings(self.allowed_tools, "allowed_tools")))
        object.__setattr__(self, "required_env", _tuple_of_strings(self.required_env, "required_env"))
        object.__setattr__(self, "risk_level", SkillRiskLevel(self.risk_level))
        object.__setattr__(self, "entrypoint", str(self.entrypoint or "").strip())
        object.__setattr__(self, "enabled", bool(self.enabled))
        object.__setattr__(self, "metadata", dict(self.metadata or {}))

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "SkillManifest":
        return cls(**dict(payload))

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["permissions"] = list(self.permissions)
        payload["allowed_tools"] = list(self.allowed_tools)
        payload["required_env"] = list(self.required_env)
        payload["risk_level"] = self.risk_level.value
        return payload

    def public_env_requirements(self) -> tuple[str, ...]:
        """Return only env variable names; values are never read or exposed."""
        return self.required_env


__all__ = ["SkillManifest"]
