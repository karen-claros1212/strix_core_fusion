from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import re
from typing import Any

RISK_ORDER = {"R0": 0, "R1": 1, "R2": 2, "R3": 3, "R4": 4, "R5": 5}


class RecoveryPolicyError(ValueError):
    pass


@dataclass(frozen=True)
class SessionRecoveryPolicy:
    default_budget_chars: int = 1600
    ttl_seconds: int = 3600
    non_authoritative: bool = True
    execution_allowed: bool = False

    def metadata(self) -> dict[str, Any]:
        return {
            "non_authoritative": True,
            "execution_allowed": False,
            "instruction_role": "untrusted_background_context",
            "may_override_policy": False,
            "may_downgrade_risk": False,
            "prompt_security_required": True,
            "mission_policy_required": True,
            "sandbox_controller_required": True,
        }

    def assert_recoverable_metadata(self, metadata: dict[str, Any]) -> None:
        if metadata.get("non_authoritative") is not True:
            raise RecoveryPolicyError("snapshot_context_not_non_authoritative")
        if metadata.get("execution_allowed") is not False:
            raise RecoveryPolicyError("snapshot_execution_not_allowed")
        if metadata.get("may_override_policy") is not False:
            raise RecoveryPolicyError("snapshot_policy_override_not_allowed")
        if metadata.get("may_downgrade_risk") is not False:
            raise RecoveryPolicyError("snapshot_risk_downgrade_not_allowed")

    def is_expired(self, expires_at: str, now: datetime | None = None) -> bool:
        current = now or datetime.now(timezone.utc)
        try:
            expiry = datetime.fromisoformat(str(expires_at).replace("Z", "+00:00"))
        except Exception as exc:  # noqa: BLE001 - invalid metadata is a recovery policy failure
            raise RecoveryPolicyError("invalid_snapshot_expiry") from exc
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        return current >= expiry

    def effective_risk(self, live_risk: str | None, recovered_risk: str | None) -> str:
        live = self._risk_value(live_risk or recovered_risk or "R0")
        recovered = self._risk_value(recovered_risk or live)
        return recovered if RISK_ORDER.get(recovered, 0) > RISK_ORDER.get(live, 0) else live

    def enforce_recovered_risk(self, live_risk: str | None, recovered_risk: str | None) -> str:
        # Recovered context is allowed to preserve/escalate risk metadata, never downgrade an R4/R5 live intent.
        return self.effective_risk(live_risk, recovered_risk)

    def _risk_value(self, risk: Any) -> str:
        value = str(getattr(risk, "value", risk) or "R0").upper()
        return value if value in RISK_ORDER else "R0"


INSTRUCTION_ROLE_RE = re.compile(r"(?im)^\s*(system|developer|tool|assistant)\s*:")
INSTRUCTION_PHRASE_RE = re.compile(
    r"(?i)\b(ignore (all )?(previous|prior) instructions|you are now|act as system|developer message|system instruction|bypass (missionpolicy|promptsecurity|sandboxcontroller))\b"
)


def neutralize_instruction_text(text: str) -> str:
    """Make recovered summaries inert background text, not executable instructions."""
    source = "" if text is None else str(text)
    lines: list[str] = []
    for line in source.splitlines():
        line = INSTRUCTION_ROLE_RE.sub(r"quoted_\1_role:", line)
        line = INSTRUCTION_PHRASE_RE.sub("[NEUTRALIZED_RECOVERED_INSTRUCTION]", line)
        lines.append(line)
    return "\n".join(lines)
