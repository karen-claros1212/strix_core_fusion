from .telegram_types import MissionRequest, RiskLevel
from ..llm.action_normalizer import canonicalize_action


class MissionPolicy:
    def classify_risk(self, request: MissionRequest) -> RiskLevel:
        """Classify risk based on action and arguments."""
        action = canonicalize_action(
            request.action_type,
            request.target,
            request.arguments,
            getattr(request, "raw_text", ""),
        )

        if action == "delete":
            return RiskLevel.R5
        if action in {"create", "deploy", "run", "execute"}:
            return RiskLevel.R4
        if action in {"scan", "backup", "collect", "report"}:
            return RiskLevel.R3
        if action in {"status", "show", "list", "get"}:
            return RiskLevel.R0
        return RiskLevel.R1

    def requires_approval(self, risk_level: RiskLevel) -> bool:
        """Check if approval is required."""
        return risk_level in {RiskLevel.R4, RiskLevel.R5}

    def is_blocked(self, risk_level: RiskLevel) -> bool:
        return risk_level == RiskLevel.R5
