import json

from .telegram_types import MissionStatus
from .command_parser import CommandParser
from .mission_policy import MissionPolicy
from .approval_workflow import ApprovalWorkflow
from .sandbox_dispatcher import SandboxDispatcher
from .evidence_logger import EvidenceLogger
from .replay_guard import ReplayGuard
from .rate_limiter import RateLimiter
from .telegram_security import TelegramSecurity
from .mission_parser import MissionParser


class TelegramMissionOperator:
    def __init__(self, config, gateway):
        self.config = config
        self.gateway = gateway
        self.command_parser = CommandParser()
        self.mission_parser = MissionParser()
        self.policy = MissionPolicy()
        self.approval_workflow = ApprovalWorkflow(expiration_minutes=config.approval_timeout_minutes)
        self.security = TelegramSecurity(config)
        self.evidence_logger = EvidenceLogger(audit=None, security=self.security)
        self.replay_guard = ReplayGuard()
        self.rate_limiter = RateLimiter(max_requests=10, window_seconds=60)
        self.sandbox_dispatcher = SandboxDispatcher(sandbox_controller=None)

    def _serialize_response(self, payload: dict) -> str:
        return json.dumps(payload, sort_keys=True)

    def _mission_response(self, request, status: str, result: dict | None = None, approval_id: str | None = None) -> str:
        payload = {
            "mission_id": request.mission_id,
            "status": status,
            "risk_level": request.risk_level.value,
            "action_type": request.action_type,
            "target": request.target,
            "approval_id": approval_id,
            "result": result or {},
            "message": "requires approval" if status == "approval_required" else status.replace("_", " "),
        }
        return self._serialize_response(payload)

    async def handle_message(self, chat_id: str, user_id: str, text: str) -> str:
        if not self.rate_limiter.is_allowed(user_id):
            return "Rate limit exceeded. Please try again later."

        if not self.security.validate_user(user_id):
            return "Unauthorized user."

        normalized_text = (text or "").strip()
        parsed = self.command_parser.parse(normalized_text)

        if parsed is not None and not getattr(parsed, 'known', False):
            return f"Error: Unknown command: {parsed.command}"

        if parsed is not None and getattr(parsed, 'command', '') == 'status':
            return self._serialize_response({"status": "ok", "message": "System Status: Operational"})

        if parsed is not None and getattr(parsed, 'command', '') == 'mission':
            mission_text = ' '.join(getattr(parsed, 'args', []))
        elif parsed is None:
            mission_text = normalized_text
        else:
            return "Unknown command."

        request = self.mission_parser.parse(mission_text, requester_id=user_id, chat_id=chat_id)
        request.risk_level = self.policy.classify_risk(request)

        if self.replay_guard.is_duplicate(request.mission_id):
            return "Duplicate mission detected."

        if self.policy.is_blocked(request.risk_level):
            request.status = MissionStatus.REJECTED
            result = {"status": "blocked", "executed": False, "reason": "risk_r5_blocked"}
            self.evidence_logger.log_mission(request, result)
            return self._mission_response(request, "blocked", result=result)

        if self.policy.requires_approval(request.risk_level):
            request.status = MissionStatus.PENDING
            approval_id = self.approval_workflow.create_approval(request.mission_id)
            request.approval_id = approval_id
            result = {"status": "approval_required", "executed": False, "approval_id": approval_id}
            self.evidence_logger.log_mission(request, result)
            return self._mission_response(
                request,
                "approval_required",
                result=result,
                approval_id=approval_id,
            )

        request.status = MissionStatus.EXECUTING
        result = self.sandbox_dispatcher.dispatch(request)
        request.status = MissionStatus.COMPLETED if result.get("status") == "dry_run" else MissionStatus.FAILED
        self.evidence_logger.log_mission(request, result)
        self.replay_guard.mark_executed(request.mission_id)
        return self._mission_response(request, result.get("status", "dry_run"), result=result)
