from __future__ import annotations

from ..policy import DangerousActionPolicy
from .skill_manifest import SkillManifest
from .skill_registry import SkillRegistry
from .skill_types import SkillPolicyDecision, SkillPolicyStatus, SkillRiskLevel


class SkillPolicy:
    """Policy gate for skill metadata. It grants no execution authority."""

    def __init__(self, registry: SkillRegistry | None = None, dangerous_policy: DangerousActionPolicy | None = None):
        self.registry = registry or SkillRegistry()
        self.dangerous_policy = dangerous_policy or DangerousActionPolicy()

    def decide(self, skill_name: str, action_text: str = "", context: dict | None = None) -> SkillPolicyDecision:
        manifest = self.registry.get(skill_name)
        if manifest is None:
            return self._decision(False, True, False, SkillPolicyStatus.BLOCKED, "unknown_skill_blocked", skill_name, SkillRiskLevel.R4)
        return self.decide_manifest(manifest, action_text=action_text, context=context)

    def decide_manifest(self, manifest: SkillManifest, action_text: str = "", context: dict | None = None) -> SkillPolicyDecision:
        if not manifest.enabled:
            return self._decision(False, True, False, SkillPolicyStatus.BLOCKED, "disabled_skill_blocked", manifest.name, manifest.risk_level)

        joined = " ".join(
            [
                action_text or "",
                manifest.description,
                " ".join(manifest.permissions),
                " ".join(str(v) for v in manifest.metadata.values()),
            ]
        )
        if self._requests_secret_directly(manifest):
            return self._decision(False, True, False, SkillPolicyStatus.BLOCKED, "direct_secret_request_blocked", manifest.name, manifest.risk_level)
        if self._attempts_control_bypass(manifest):
            return self._decision(False, True, False, SkillPolicyStatus.BLOCKED, "mission_policy_or_sandbox_bypass_blocked", manifest.name, SkillRiskLevel.R5)
        dangerous = self.dangerous_policy.evaluate(joined)
        if dangerous.blocked:
            return self._decision(False, True, False, SkillPolicyStatus.BLOCKED, dangerous.reason, manifest.name, SkillRiskLevel.R5)
        if manifest.risk_level == SkillRiskLevel.R5:
            return self._decision(False, True, False, SkillPolicyStatus.BLOCKED, "risk_r5_blocked", manifest.name, manifest.risk_level)
        if manifest.risk_level == SkillRiskLevel.R4 or dangerous.approval_required:
            return self._decision(False, False, True, SkillPolicyStatus.APPROVAL_REQUIRED, "risk_r4_requires_approval", manifest.name, SkillRiskLevel.R4)
        return self._decision(True, False, False, SkillPolicyStatus.ALLOWED, "allowed_metadata_only_no_execution", manifest.name, manifest.risk_level)

    @staticmethod
    def _requests_secret_directly(manifest: SkillManifest) -> bool:
        text = " ".join([manifest.description, " ".join(manifest.permissions), " ".join(manifest.allowed_tools), str(manifest.metadata)]).lower()
        return any(marker in text for marker in ("read_secret", "secret_read", "dump_env", "env_dump", "token_value", "raw_secret"))

    @staticmethod
    def _attempts_control_bypass(manifest: SkillManifest) -> bool:
        text = " ".join([manifest.description, " ".join(manifest.permissions), str(manifest.metadata)]).lower()
        return any(marker in text for marker in ("bypass", "disable_sandbox", "skip_missionpolicy", "skip missionpolicy", "without sandboxcontroller"))

    @staticmethod
    def _decision(allowed: bool, blocked: bool, approval_required: bool, status: SkillPolicyStatus, reason: str, skill_name: str, risk_level: SkillRiskLevel) -> SkillPolicyDecision:
        return SkillPolicyDecision(
            allowed=allowed,
            blocked=blocked,
            approval_required=approval_required,
            status=status,
            reason=reason,
            skill_name=(skill_name or "").strip().lower(),
            risk_level=risk_level,
            evidence_metadata={"metadata_only": True, "execution_allowed": False},
        )


__all__ = ["SkillPolicy"]
