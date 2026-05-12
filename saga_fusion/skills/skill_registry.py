from __future__ import annotations

from .skill_manifest import SkillManifest
from .skill_validator import SkillValidator


class SkillRegistry:
    """In-memory registry for validated skill/plugin metadata only."""

    def __init__(self, validator: SkillValidator | None = None):
        self.validator = validator or SkillValidator()
        self._skills: dict[str, SkillManifest] = {}

    def register(self, manifest: SkillManifest) -> SkillManifest:
        self.validator.validate(manifest)
        name = manifest.name
        if name in self._skills:
            raise ValueError(f"duplicate skill manifest: {name}")
        self._skills[name] = manifest
        return manifest

    def get(self, name: str) -> SkillManifest | None:
        return self._skills.get((name or "").strip().lower())

    def list_enabled(self) -> list[SkillManifest]:
        return [manifest for manifest in self._skills.values() if manifest.enabled]

    def disable(self, name: str) -> SkillManifest:
        manifest = self._require(name)
        updated = SkillManifest(**{**manifest.to_dict(), "enabled": False})
        self._skills[manifest.name] = updated
        return updated

    def enable(self, name: str) -> SkillManifest:
        manifest = self._require(name)
        updated = SkillManifest(**{**manifest.to_dict(), "enabled": True})
        self.validator.validate(updated)
        self._skills[manifest.name] = updated
        return updated

    def _require(self, name: str) -> SkillManifest:
        manifest = self.get(name)
        if manifest is None:
            raise KeyError(f"unknown skill: {name}")
        return manifest


__all__ = ["SkillRegistry"]
