import json

from .telegram_types import MissionRequest, MissionStatus
from .command_parser import CommandParser
from .mission_policy import MissionPolicy
from .approval_workflow import ApprovalWorkflow
from .sandbox_dispatcher import SandboxDispatcher
from .evidence_logger import EvidenceLogger
from .replay_guard import ReplayGuard
from .rate_limiter import RateLimiter
from .telegram_security import TelegramSecurity
from .mission_parser import MissionParser
from ..llm.llm_router import LLMRouter
from ..prompt_security import PromptRiskLevel, PromptSecurityLayer
from ..tool_routing import ToolRouter


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
        self.rate_limiter = RateLimiter(max_requests=getattr(config, "rate_limit_per_minute", 10), window_seconds=60)
        self.sandbox_dispatcher = SandboxDispatcher(sandbox_controller=None)
        self.llm_router = LLMRouter()
        self.prompt_security = PromptSecurityLayer()
        self.tool_router = ToolRouter()

    def _serialize_response(self, payload: dict) -> str:
        redacted = self.security.redact_secrets(json.dumps(payload, sort_keys=True))
        return redacted

    def _mission_response(self, request, status: str, result: dict | None = None, approval_id: str | None = None) -> str:
        payload = {
            "mission_id": request.mission_id,
            "status": status,
            "risk_level": request.risk_level.value,
            "action_type": request.action_type,
            "target": request.target,
            "approval_id": approval_id,
            "action_hash": request.action_hash,
            "result": result or {},
            "message": "requires approval" if status == "approval_required" else status.replace("_", " "),
        }
        return self._serialize_response(payload)

    def _request_payload(self, request):
        return {
            "mission_id": request.mission_id,
            "action_type": request.action_type,
            "target": request.target,
            "arguments": request.arguments,
            "risk_level": request.risk_level.value,
        }

    async def handle_message(self, chat_id: str, user_id: str, text: str) -> str:
        self.evidence_logger.log_incoming_message(chat_id, user_id, text)

        if not self.rate_limiter.is_allowed(user_id):
            self.evidence_logger.log_authorization_decision(chat_id, user_id, False)
            return "Rate limit exceeded. Please try again later."

        authorized = self.security.validate_user(user_id)
        self.evidence_logger.log_authorization_decision(chat_id, user_id, authorized)
        if not authorized:
            return "DENIED: Unauthorized user."

        normalized_text = (text or "").strip()
        parsed = self.command_parser.parse(normalized_text)

        if parsed is not None and not getattr(parsed, "known", False):
            return f"Error: Unknown command: {parsed.command}"

        if parsed is not None and getattr(parsed, "command", "") == "status":
            return self._serialize_response({"status": "ok", "message": "System Status: Operational"})

        if parsed is not None and getattr(parsed, "command", "") == "mission":
            mission_text = " ".join(getattr(parsed, "args", []))
            request = self.mission_parser.parse(mission_text, requester_id=user_id, chat_id=chat_id)
        elif parsed is None:
            prompt_guard = self.prompt_security.guard_for_llm(
                normalized_text,
                context={"chat_id": str(chat_id), "user_id": str(user_id)},
            )
            decision = prompt_guard["decision"]
            self.evidence_logger._record(
                "prompt_security_decision",
                {
                    "chat_id": str(chat_id),
                    "user_id": str(user_id),
                    "risk_level": decision.risk_level.value,
                    "reason": decision.reason,
                    "threats": [threat.value for threat in decision.threats],
                    "matched_patterns": decision.matched_patterns,
                },
            )
            if decision.risk_level == PromptRiskLevel.BLOCK:
                return self._serialize_response(
                    {
                        "status": "blocked",
                        "risk_level": "prompt_security",
                        "reason": decision.reason,
                        "executed": False,
                        "message": "blocked by prompt security",
                    }
                )
            mission_data = self.llm_router.build_mission_from_natural_language(
                prompt_guard["sanitized"].sanitized_text,
                context={
                    "chat_id": str(chat_id),
                    "user_id": str(user_id),
                    "prompt_security": {
                        "risk_level": decision.risk_level.value,
                        "reason": decision.reason,
                        "threats": [threat.value for threat in decision.threats],
                    },
                },
            )
            request = MissionRequest(
                requester_id=str(user_id),
                chat_id=str(chat_id),
                raw_text=normalized_text,
                action_type=str(mission_data.get("action_type") or "status"),
                target=str(mission_data.get("target") or ""),
                arguments=str(mission_data.get("arguments") or mission_data.get("target") or ""),
            )
        else:
            return "Unknown command."

        request.risk_level = self.policy.classify_risk(request)
        tool_decision = self.tool_router.route_tool_request(request)
        tool_plan = self.tool_router.build_execution_plan(tool_decision, request)
        self.evidence_logger._record(
            "tool_route_decision",
            {
                "mission_id": request.mission_id,
                "tool_name": tool_decision.tool_name,
                "category": tool_decision.category.value,
                "route": tool_decision.route,
                "risk_level": tool_decision.risk_level.value,
                "sandbox_required": tool_decision.sandbox_required,
                "approval_required": tool_decision.approval_required,
                "blocked": tool_decision.blocked,
                "reason": tool_decision.reason,
                "dry_run": tool_plan.dry_run,
                "execution_allowed": tool_plan.execution_allowed,
            },
        )
        payload = self._request_payload(request)
        request.action_hash = self.approval_workflow.compute_action_hash(payload)

        if self.replay_guard.is_duplicate(request.mission_id):
            return "Duplicate mission detected."

        if self.policy.is_blocked(request.risk_level):
            request.status = MissionStatus.REJECTED
            result = {"status": "blocked", "executed": False, "reason": "risk_r5_blocked"}
            self.evidence_logger.log_policy_decision(request.mission_id, request.risk_level, "blocked")
            self.evidence_logger.log_mission(request, result)
            return self._mission_response(request, "blocked", result=result)

        if self.policy.requires_approval(request.risk_level):
            request.status = MissionStatus.PENDING
            approval_id = self.approval_workflow.create_approval(request.mission_id, action_payload=payload)
            request.approval_id = approval_id
            request.action_hash = self.approval_workflow.get_action_hash(approval_id)
            result = {
                "status": "approval_required",
                "executed": False,
                "approval_id": approval_id,
                "action_hash": request.action_hash,
            }
            self.evidence_logger.log_policy_decision(request.mission_id, request.risk_level, "approval_required")
            self.evidence_logger.log_approval_decision(approval_id, "created", request.action_hash)
            self.evidence_logger.log_mission(request, result)
            return self._mission_response(request, "approval_required", result=result, approval_id=approval_id)

        request.status = MissionStatus.EXECUTING
        result = self.sandbox_dispatcher.dispatch(request)
        request.status = MissionStatus.COMPLETED if result.get("status") == "dry_run" else MissionStatus.FAILED
        self.evidence_logger.log_policy_decision(request.mission_id, request.risk_level, "sandbox_dispatch")
        self.evidence_logger.log_sandbox_dispatch_result(request.mission_id, result)
        self.evidence_logger.log_mission(request, result)
        self.replay_guard.mark_executed(request.mission_id)
        return self._mission_response(request, result.get("status", "dry_run"), result=result)
