from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class PromptThreatType(str, Enum):
    IGNORE_PREVIOUS_INSTRUCTIONS = 'ignore_previous_instructions'
    SYSTEM_PROMPT_EXFILTRATION = 'system_prompt_exfiltration'
    SECRET_EXFILTRATION = 'secret_exfiltration'
    TOOL_POLICY_BYPASS = 'tool_policy_bypass'
    ROLEPLAY_BYPASS = 'roleplay_bypass'
    INSTRUCTION_OVERRIDE = 'instruction_override'
    DATA_EXFILTRATION = 'data_exfiltration'
    UNSAFE_AUTONOMY_REQUEST = 'unsafe_autonomy_request'
    BENIGN = 'benign'


class PromptRiskLevel(str, Enum):
    ALLOW = 'allow'
    WARN = 'warn'
    BLOCK = 'block'
    ESCALATE_TO_POLICY = 'escalate_to_policy'


@dataclass(frozen=True)
class PromptSecurityDecision:
    risk_level: PromptRiskLevel
    threats: list[PromptThreatType] = field(default_factory=list)
    reason: str = 'benign'
    matched_patterns: list[str] = field(default_factory=list)
    safe_to_call_llm: bool = True
    metadata: dict = field(default_factory=dict)

    @property
    def blocked(self) -> bool:
        return self.risk_level == PromptRiskLevel.BLOCK


@dataclass(frozen=True)
class SanitizedPrompt:
    original_text: str
    sanitized_text: str
    suspicious_segments: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
