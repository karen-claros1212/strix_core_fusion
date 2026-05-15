"""
strix_core_gateway.py — Gateway STRIX oficial → Telegram
Lee respuesta de state.final_result, no de tool calls intermedios.
Timeout 180s para dejar que STRIX complete el análisis.
"""
from __future__ import annotations
import asyncio, inspect, logging
from dataclasses import dataclass, field
from typing import Any

_log = logging.getLogger(__name__)

@dataclass(frozen=True)
class StrixCoreGatewayResult:
    available: bool
    handled: bool
    response: str = ""
    reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class _Session:
    chat_id: str
    user_id: str
    agent: Any
    task: asyncio.Task | None = None
    assistant_seen: int = 0
    started: bool = False

class StrixCoreGateway:
    def __init__(self, *, enabled: bool = True, agent_timeout: float = 180.0):
        self.enabled = enabled
        self.agent_timeout = agent_timeout
        self._imports = None
        self._unavailable_reason = ""
        self._sessions = {}

    def _load_imports(self):
        if not self.enabled:
            self._unavailable_reason = "disabled"
            return None
        if self._imports is not None:
            return self._imports
        try:
            from strix.agents.StrixAgent import StrixAgent
            from strix.llm.config import LLMConfig
            from strix.telemetry.tracer import Tracer, set_global_tracer
            self._imports = (StrixAgent, LLMConfig, Tracer, set_global_tracer)
            return self._imports
        except Exception as exc:
            self._unavailable_reason = f"import_error:{exc}"
            return None

    def is_available(self):
        return self._load_imports() is not None

    @property
    def unavailable_reason(self):
        self._load_imports()
        return self._unavailable_reason

    async def handle_message(self, chat_id, user_id, text):
        imports = self._load_imports()
        if imports is None:
            return StrixCoreGatewayResult(available=False, handled=False, reason=self._unavailable_reason)
        text = (text or "").strip()
        if not text:
            return StrixCoreGatewayResult(available=True, handled=False, reason="empty")
        try:
            session = await self._get_or_create_session(str(chat_id), str(user_id), text, imports)
            await self._inject_user_message(session, text)
            if session.task is not None:
                try:
                    await asyncio.wait_for(asyncio.shield(session.task), timeout=self.agent_timeout)
                except asyncio.TimeoutError:
                    _log.info("agent_timeout %.0fs", self.agent_timeout)
            response = self._read_response(session)
            return StrixCoreGatewayResult(available=True, handled=True, response=response, reason="ok")
        except Exception as exc:
            return StrixCoreGatewayResult(available=False, handled=False, reason=f"error:{exc}")

    async def _get_or_create_session(self, chat_id, user_id, text, imports):
        key = chat_id
        if key in self._sessions:
            return self._sessions[key]
        StrixAgent, LLMConfig, Tracer, set_global_tracer = imports
        llm_config = self._make_llm_config(LLMConfig)
        agent = StrixAgent({"llm_config": llm_config})
        tracer = self._instantiate_tracer(Tracer, chat_id)
        if tracer and callable(set_global_tracer):
            maybe = set_global_tracer(tracer)
            if inspect.isawaitable(maybe):
                await maybe
        session = _Session(chat_id=chat_id, user_id=user_id, agent=agent)
        session.assistant_seen = len(self._assistant_messages(agent))
        scan_config = {"user_instructions": text, "targets": [], "interactive": False}
        execute_scan = getattr(agent, "execute_scan", None)
        if callable(execute_scan):
            result = execute_scan(scan_config)
            if inspect.isawaitable(result):
                session.task = asyncio.ensure_future(result)
        session.started = True
        self._sessions[key] = session
        return session

    async def _inject_user_message(self, session, text):
        if not session.started:
            return
        state = getattr(session.agent, "state", None)
        if state is None:
            return
        add_message = getattr(state, "add_message", None)
        if callable(add_message):
            maybe = add_message("user", text)
            if inspect.isawaitable(maybe):
                await maybe
            return
        msg = {"role": "user", "content": text}
        for attr in ("messages", "history"):
            lst = getattr(state, attr, None)
            if isinstance(lst, list):
                lst.append(msg)
                break

    def _read_response(self, session):
        """Lee respuesta final: final_result, execution_summary o último assistant."""
        s = getattr(session.agent, "state", None)
        # 1. final_result si el scan completó
        if s and s.final_result:
            if isinstance(s.final_result, dict):
                for campo in ("output", "result", "summary", "report"):
                    v = s.final_result.get(campo, "")
                    if v:
                        return str(v)
            return str(s.final_result)
        # 2. execution_summary
        if s:
            try:
                summary = s.get_execution_summary()
                if summary and isinstance(summary, dict):
                    for campo in ("final_result", "result", "summary"):
                        v = summary.get(campo, "")
                        if v:
                            return str(v)
            except Exception:
                pass
        # 3. último assistant message
        messages = self._assistant_messages(session.agent)
        for m in reversed(messages):
            content = self._message_content(m)
            if content:
                return content
        return "STRIX_OFFICIAL_NO_ASSISTANT_RESPONSE"

    def _assistant_messages(self, agent):
        state = getattr(agent, "state", None)
        candidates = []
        for attr in ("messages", "history", "conversation_history"):
            val = getattr(state, attr, None) if state else None
            if isinstance(val, list):
                candidates.extend(val)
        fn = getattr(state, "get_conversation_history", None) if state else None
        if callable(fn):
            try:
                v = fn()
                if isinstance(v, list):
                    candidates.extend(v)
            except Exception:
                pass
        return [m for m in candidates if str(m.get("role","") if isinstance(m,dict) else getattr(m,"role","")).lower()=="assistant"]

    @staticmethod
    def _message_content(item):
        import re
        if isinstance(item, dict):
            raw = str(item.get("content") or item.get("text") or "").strip()
        else:
            raw = str(getattr(item, "content", "") or getattr(item, "text", "")).strip()
        clean = re.sub(r"<function=[^>]+>.*?</function>", "", raw, flags=re.DOTALL)
        clean = re.sub(r"<parameter=[^>]+>.*?</parameter>", "", clean, flags=re.DOTALL)
        return clean.strip()

    @staticmethod
    def _make_llm_config(LLMConfig):
        for kwargs in ({"interactive": False}, {"interactive": True}, {}):
            try:
                return LLMConfig(**kwargs)
            except TypeError:
                continue
        return LLMConfig()

    @staticmethod
    def _instantiate_tracer(Tracer, chat_id):
        try:
            return Tracer(session_id=f"tg-{chat_id}")
        except Exception:
            try:
                return Tracer()
            except Exception:
                return None
