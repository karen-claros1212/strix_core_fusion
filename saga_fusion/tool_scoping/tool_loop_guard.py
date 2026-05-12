from __future__ import annotations

import json
from dataclasses import replace

from saga_fusion.tool_routing.tool_routing_types import ToolCategory, ToolRisk, ToolRouteDecision

from .tool_scope_types import ToolLoopGuardConfig, ToolLoopState


class ToolLoopGuard:
    """Bound tool-routing loops per mission; metadata-only guardrail."""

    def __init__(self, max_tool_calls: int = 20, max_repeated_tool_calls: int = 3):
        self.config = ToolLoopGuardConfig(max_tool_calls=max_tool_calls, max_repeated_tool_calls=max_repeated_tool_calls)
        self._states: dict[str, ToolLoopState] = {}

    def check(self, tool_name: str, args=None, context: dict | None = None) -> ToolRouteDecision | None:
        mission_id = self._mission_id(context)
        normalized_tool = str(tool_name or "unknown").strip().lower()
        signature = self._signature(normalized_tool, args)
        state = self._states.get(mission_id, ToolLoopState(mission_id=mission_id))
        evidence = {
            "mission_id": mission_id,
            "tool_name": normalized_tool,
            "signature": signature,
            "total_calls": state.total_calls,
            "max_tool_calls": self.config.max_tool_calls,
            "max_repeated_tool_calls": self.config.max_repeated_tool_calls,
            "active_stack": list(state.active_stack),
            "metadata_only": True,
            "execution_allowed": False,
        }

        active_stack = tuple(str(item or "").strip().lower() for item in (context or {}).get("active_tool_stack", state.active_stack))
        if normalized_tool in active_stack:
            evidence["active_stack"] = list(active_stack)
            return self._blocked(normalized_tool, "recursive_tool_call_blocked", evidence)

        prospective_total = state.total_calls + 1
        if prospective_total > self.config.max_tool_calls:
            evidence["attempted_total_calls"] = prospective_total
            return self._blocked(normalized_tool, "max_tool_calls_exceeded", evidence)

        consecutive_repeats = self._consecutive_repeats(state.call_signatures, signature) + 1
        if consecutive_repeats > self.config.max_repeated_tool_calls:
            evidence["repeated_tool_calls"] = consecutive_repeats
            return self._blocked(normalized_tool, "repeated_tool_call_loop_blocked", evidence)

        updated = replace(
            state,
            total_calls=prospective_total,
            repeated_calls=consecutive_repeats,
            call_signatures=state.call_signatures + (signature,),
        )
        self._states[mission_id] = updated
        return None

    def reset(self, mission_id: str = "default") -> None:
        self._states.pop(str(mission_id or "default"), None)

    def state_for(self, mission_id: str = "default") -> ToolLoopState:
        return self._states.get(str(mission_id or "default"), ToolLoopState(mission_id=str(mission_id or "default")))

    @staticmethod
    def _mission_id(context: dict | None) -> str:
        return str((context or {}).get("mission_id") or "default").strip() or "default"

    @staticmethod
    def _signature(tool_name: str, args=None) -> str:
        safe_args = args if isinstance(args, dict) else {"value": str(args or "")}
        try:
            encoded = json.dumps(safe_args, sort_keys=True, default=str, separators=(",", ":"))
        except TypeError:
            encoded = json.dumps(str(safe_args), sort_keys=True)
        return f"{tool_name}:{encoded}"

    @staticmethod
    def _consecutive_repeats(signatures: tuple[str, ...], signature: str) -> int:
        count = 0
        for existing in reversed(signatures):
            if existing != signature:
                break
            count += 1
        return count

    @staticmethod
    def _blocked(tool_name: str, reason: str, evidence: dict) -> ToolRouteDecision:
        return ToolRouteDecision(False, True, False, ToolRisk.R4, tool_name, ToolCategory.UNKNOWN, "blocked", True, reason, evidence)


__all__ = ["ToolLoopGuard"]
