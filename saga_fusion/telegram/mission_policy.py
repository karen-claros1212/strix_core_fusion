from .telegram_types import MissionRequest, RiskLevel


class MissionPolicy:
    def classify_risk(self, request: MissionRequest) -> RiskLevel:
        """Classify risk based on action and arguments."""
        action = (request.action_type or "").lower()
        args = (request.arguments or "").lower()
        target = (request.target or "").lower()
        combined = " ".join(part for part in [action, target, args] if part)

        if "rm -rf" in combined or action in {"delete", "destroy", "wipe"}:
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
