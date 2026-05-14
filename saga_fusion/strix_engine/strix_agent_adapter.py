from __future__ import annotations

import asyncio
import inspect
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass(frozen=True)
class StrixAgentAdapterResult:
    """Result returned by the optional real STRIX agent adapter."""

    available: bool
    handled: bool
    response: str = ""
    reason: str = ""
    routed_by: str = "real_strix_agent"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class _StrixAgentSession:
    chat_id: str
    user_id: str
    agent: Any
    tracer: Any = None
    task: asyncio.Task | None = None
    assistant_seen: int = 0
    started: bool = False


class StrixAgentAdapter:
    """Optional bridge from Telegram lab messages into the real STRIX agent.

    The real STRIX classes are imported lazily and optionally.  Repositories or
    test environments that do not ship ``strix.agents.StrixAgent`` remain fully
    functional because the adapter reports ``available=False`` and callers can
    fall back to the existing Saga Fusion mission pipeline.
    """

    def __init__(
        self,
        *,
        imports_loader: Callable[[], tuple[Any, Any, Any, Callable[[Any], Any] | None]] | None = None,
        enabled: bool = True,
    ):
        self.enabled = enabled
        self._imports_loader = imports_loader or self._default_imports_loader
        self._imports: tuple[Any, Any, Any, Callable[[Any], Any] | None] | None = None
        self._unavailable_reason = ""
        self._sessions: dict[str, _StrixAgentSession] = {}

    @staticmethod
    def _default_imports_loader() -> tuple[Any, Any, Any, Callable[[Any], Any] | None]:
        from strix.agents.StrixAgent import StrixAgent  # type: ignore
        from strix.llm.config import LLMConfig  # type: ignore
        from strix.telemetry.tracer import Tracer, set_global_tracer  # type: ignore

        return StrixAgent, LLMConfig, Tracer, set_global_tracer

    def _load_imports(self) -> tuple[Any, Any, Any, Callable[[Any], Any] | None] | None:
        if not self.enabled:
            self._unavailable_reason = "adapter_disabled"
            return None
        if self._imports is not None:
            return self._imports
        try:
            self._imports = self._imports_loader()
            return self._imports
        except Exception as exc:  # pragma: no cover - exact import error varies by deployment
            self._unavailable_reason = f"strix_agent_unavailable:{type(exc).__name__}"
            return None

    @property
    def unavailable_reason(self) -> str:
        self._load_imports()
        return self._unavailable_reason

    def is_available(self) -> bool:
        return self._load_imports() is not None

    async def handle_message(self, chat_id: str, user_id: str, text: str) -> StrixAgentAdapterResult:
        imports = self._load_imports()
        if imports is None:
            return StrixAgentAdapterResult(
                available=False,
                handled=False,
                reason=self._unavailable_reason or "strix_agent_unavailable",
                metadata=self._safe_metadata(chat_id, user_id),
            )

        normalized_text = (text or "").strip()
        if not normalized_text:
            return StrixAgentAdapterResult(
                available=True,
                handled=False,
                reason="empty_message",
                metadata=self._safe_metadata(chat_id, user_id),
            )

        try:
            session = await self._get_or_create_session(str(chat_id), str(user_id), normalized_text, imports)
            await self._deliver_user_message(session, normalized_text, first_message=not session.started)
            if not session.started:
                session.started = True
            # Let faked async execute_scan/resume callbacks run once without
            # blocking a real long-running agent loop.
            await asyncio.sleep(0)
            assistant_response = self._latest_new_assistant_response(session)
            if not assistant_response:
                assistant_response = "STRIX agent session active; awaiting assistant response."
            return StrixAgentAdapterResult(
                available=True,
                handled=True,
                response=assistant_response,
                reason="handled_by_real_strix_agent",
                metadata={
                    **self._safe_metadata(chat_id, user_id),
                    "session_id": self._session_key(chat_id),
                    "saga_control_layer": True,
                    "execution_allowed": False,
                    "executed": False,
                    "lab_mode": True,
                },
            )
        except Exception as exc:
            return StrixAgentAdapterResult(
                available=False,
                handled=False,
                reason=f"strix_agent_error:{type(exc).__name__}",
                metadata=self._safe_metadata(chat_id, user_id),
            )

    async def _get_or_create_session(
        self,
        chat_id: str,
        user_id: str,
        initial_text: str,
        imports: tuple[Any, Any, Any, Callable[[Any], Any] | None],
    ) -> _StrixAgentSession:
        key = self._session_key(chat_id)
        if key in self._sessions:
            return self._sessions[key]

        StrixAgent, LLMConfig, Tracer, set_global_tracer = imports
        llm_config = self._instantiate(LLMConfig, interactive=True)
        agent_config = {
            "llm_config": llm_config,
            "interactive": True,
            "lab_mode": True,
            "telegram_chat_id": str(chat_id),
            "telegram_user_id": str(user_id),
            "execution_allowed": False,
            "dry_run": True,
        }
        agent = self._instantiate(StrixAgent, agent_config)
        tracer = self._instantiate(Tracer, session_id=f"telegram-lab-{chat_id}")
        if callable(set_global_tracer):
            maybe = set_global_tracer(tracer)
            if inspect.isawaitable(maybe):
                await maybe

        session = _StrixAgentSession(chat_id=chat_id, user_id=user_id, agent=agent, tracer=tracer)
        session.assistant_seen = len(self._assistant_messages(agent))
        scan_config = self._lab_scan_config(chat_id, user_id, initial_text)
        execute_scan = getattr(agent, "execute_scan", None)
        if callable(execute_scan):
            result = execute_scan(scan_config)
            if inspect.isawaitable(result):
                session.task = asyncio.create_task(result)
        self._sessions[key] = session
        return session

    async def _deliver_user_message(self, session: _StrixAgentSession, text: str, *, first_message: bool) -> None:
        state = getattr(session.agent, "state", None)
        if state is None:
            return
        add_message = getattr(state, "add_message", None)
        if callable(add_message):
            maybe = add_message("user", text)
            if inspect.isawaitable(maybe):
                await maybe
        else:
            message = {"role": "user", "content": text}
            if hasattr(state, "messages") and isinstance(getattr(state, "messages"), list):
                state.messages.append(message)
            elif hasattr(state, "history") and isinstance(getattr(state, "history"), list):
                state.history.append(message)
        if not first_message:
            resume = getattr(state, "resume_from_waiting", None)
            if callable(resume):
                maybe = resume()
                if inspect.isawaitable(maybe):
                    await maybe

    def _latest_new_assistant_response(self, session: _StrixAgentSession) -> str:
        assistant_messages = self._assistant_messages(session.agent)
        new_messages = assistant_messages[session.assistant_seen :]
        session.assistant_seen = len(assistant_messages)
        for item in reversed(new_messages or assistant_messages):
            content = self._message_content(item)
            if content:
                return content
        return ""

    def _assistant_messages(self, agent: Any) -> list[Any]:
        state = getattr(agent, "state", None)
        candidates: list[Any] = []
        for attr in ("messages", "history", "conversation_history"):
            value = getattr(state, attr, None) if state is not None else None
            if isinstance(value, list):
                candidates.extend(value)
        history_fn = getattr(state, "get_conversation_history", None) if state is not None else None
        if callable(history_fn):
            try:
                value = history_fn()
                if isinstance(value, list):
                    candidates.extend(value)
            except Exception:
                pass
        assistant = []
        for item in candidates:
            role = item.get("role") if isinstance(item, dict) else getattr(item, "role", "")
            if str(role).lower() == "assistant":
                assistant.append(item)
        return assistant

    @staticmethod
    def _message_content(item: Any) -> str:
        if isinstance(item, dict):
            return str(item.get("content") or item.get("text") or "").strip()
        return str(getattr(item, "content", "") or getattr(item, "text", "")).strip()

    @staticmethod
    def _instantiate(cls: Any, *args: Any, **kwargs: Any) -> Any:
        try:
            return cls(*args, **kwargs)
        except TypeError:
            if args:
                try:
                    return cls(config=args[0], **kwargs)
                except TypeError:
                    pass
            try:
                return cls(**kwargs)
            except TypeError:
                return cls()

    @staticmethod
    def _session_key(chat_id: str) -> str:
        return str(chat_id)

    @staticmethod
    def _lab_scan_config(chat_id: str, user_id: str, text: str) -> dict[str, Any]:
        return {
            "scan_id": f"telegram-lab-{uuid.uuid5(uuid.NAMESPACE_URL, f'{chat_id}:{user_id}')}",
            "mode": "telegram_lab",
            "target": "telegram_chat",
            "input": text,
            "interactive": True,
            "lab_mode": True,
            "dry_run": True,
            "execution_allowed": False,
            "executed": False,
            "non_authoritative": True,
            "chat_id": str(chat_id),
            "user_id": str(user_id),
        }

    @staticmethod
    def _safe_metadata(chat_id: str, user_id: str) -> dict[str, Any]:
        return {
            "chat_id": str(chat_id),
            "user_id": str(user_id),
            "execution_allowed": False,
            "executed": False,
            "non_authoritative": True,
        }
