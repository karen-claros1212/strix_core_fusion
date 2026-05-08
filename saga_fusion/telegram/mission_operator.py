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
from ..approval import ApprovalAudit, ApprovalRequestBuilder, ApprovalStore, ApprovalVerifier
from ..reporting import ReportBuilder, TelegramReportFormatter
from ..task_planning import TaskPlanner


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
        self.approval_store = ApprovalStore()
        self.approval_request_builder = ApprovalRequestBuilder(expiration_minutes=config.approval_timeout_minutes)
        self.approval_verifier = ApprovalVerifier(self.approval_store)
        self.approval_audit = ApprovalAudit()
        self.report_builder = ReportBuilder()
        self.telegram_report_formatter = TelegramReportFormatter()
        self.task_planner = TaskPlanner()

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

        if parsed is not None and getattr(parsed, "command", "") == "approve":
            if not getattr(parsed, "args", []):
                return self._serialize_response({"status": "blocked", "reason": "approval_id_required", "executed": False})
            approval_id = parsed.args[0]
            approval_request = self.approval_store.get(approval_id)
            action_hash = parsed.args[1] if len(parsed.args) > 1 else (approval_request.action_hash if approval_request else "")
            decision = self.approval_verifier.verify(
                approval_id,
                action_hash=action_hash,
                user_id=str(user_id),
                authorized_users=set(getattr(self.config, "allowed_user_ids", []) or []),
            )
            self.approval_audit.record("approval_verified", {"approval_id": approval_id, "status": decision.status.value, "reason": decision.reason})
            self.evidence_logger.log_approval_decision(approval_id, decision.status.value, action_hash)
            if decision.allowed:
                self.approval_store.mark_used(approval_id)
            return self._serialize_response({"status": decision.status.value.lower(), "reason": decision.reason, "approval_id": approval_id, "executed": False})

        if parsed is not None and getattr(parsed, "command", "") == "deny":
            if not getattr(parsed, "args", []):
                return self._serialize_response({"status": "blocked", "reason": "approval_id_required", "executed": False})
            approval_id = parsed.args[0]
            ok = self.approval_store.mark_denied(approval_id)
            self.approval_audit.record("approval_denied", {"approval_id": approval_id, "ok": ok, "user_id": str(user_id)})
            self.evidence_logger.log_approval_decision(approval_id, "DENIED" if ok else "NOT_FOUND")
            return self._serialize_response({"status": "denied" if ok else "blocked", "reason": "approval_denied" if ok else "approval_not_found", "approval_id": approval_id, "executed": False})

        if parsed is not None and getattr(parsed, "command", "") == "report":
            report = self.report_builder.build_mission_report(
                {"mission_id": "telegram-report", "status": "generated"},
                evidence=self.evidence_logger.records,
                audience="telegram_summary",
            )
            return self.telegram_report_formatter.format(report, artifact_ref="telegram:evidence")

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

        task_plan = self.task_planner.plan(
            getattr(request, "raw_text", "") or " ".join([request.action_type, request.target, request.arguments]),
            target=request.target,
            arguments=request.arguments,
            context={"chat_id": str(chat_id), "user_id": str(user_id)},
        )
        task_intent = self.task_planner.build_execution_intent(task_plan)
        self.evidence_logger._record(
            "task_plan_intent",
            {
                "mission_id": request.mission_id,
                "plan_id": task_plan.plan_id,
                "pattern_id": task_plan.pattern_id,
                "status": task_plan.status.value,
                "risk_level": task_plan.risk_level.value,
                "approval_required": task_plan.approval_required,
                "blocked": task_plan.blocked,
                "execution_allowed": task_intent.execution_allowed,
                "dry_run": task_intent.dry_run,
                "sandbox_mode": task_intent.sandbox_mode,
                "tool_name": task_intent.tool_name,
                "reporting_ready": task_plan.metadata.get("reporting_ready", False),
                "workflow_plan": task_plan.metadata.get("workflow_plan"),
                "reason": task_plan.reason,
            },
        )
        if task_plan.metadata.get("workflow_plan") and not task_plan.blocked:
            workflow_plan = task_plan.metadata["workflow_plan"]
            self.evidence_logger.log_policy_decision(request.mission_id, request.risk_level, "workflow_plan_only")
            return self._serialize_response({
                "status": "workflow_plan",
                "mission_id": request.mission_id,
                "pattern_id": task_plan.pattern_id,
                "workflow_id": workflow_plan.get("workflow_id"),
                "risk_level": workflow_plan.get("risk"),
                "step_count": len(workflow_plan.get("steps", [])),
                "evidence_required": workflow_plan.get("evidence_required"),
                "report_required": workflow_plan.get("report_required"),
                "execution_allowed": False,
                "executed": False,
            })

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
            approval_request = self.approval_request_builder.build(
                mission_id=request.mission_id,
                action_payload=payload,
                canonical_action=request.action_type,
                risk_level=request.risk_level.value,
                requested_by=str(user_id),
                reason="MissionPolicy classified this action as R4.",
                summary=f"Approve {request.action_type} on {request.target}",
                rollback_plan="Prepare provider-specific rollback before execution.",
                before_state="not_captured_dry_run",
                evidence_ref=f"mission:{request.mission_id}",
            )
            self.approval_store.create(approval_request)
            approval_id = approval_request.approval_id
            self.approval_workflow.approvals[approval_id] = {
                "mission_id": request.mission_id,
                "action_hash": approval_request.action_hash,
                "expires_at": approval_request.expires_at,
                "status": "PENDING",
            }
            request.approval_id = approval_id
            request.action_hash = approval_request.action_hash
            result = {
                "status": "approval_required",
                "executed": False,
                "approval_id": approval_id,
                "action_hash": request.action_hash,
                "evidence_ref": approval_request.evidence_ref,
            }
            self.evidence_logger.log_policy_decision(request.mission_id, request.risk_level, "approval_required")
            self.evidence_logger.log_approval_decision(approval_id, "created", request.action_hash)
            self.approval_audit.record("approval_request_created", {"approval_id": approval_id, "mission_id": request.mission_id, "action_hash": request.action_hash})
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
