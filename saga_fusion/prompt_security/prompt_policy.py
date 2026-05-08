from __future__ import annotations

from .prompt_injection_detector import PromptThreatMatch
from .prompt_security_types import PromptRiskLevel, PromptSecurityDecision, PromptThreatType

BLOCK_THREATS = {
    PromptThreatType.SYSTEM_PROMPT_EXFILTRATION,
    PromptThreatType.SECRET_EXFILTRATION,
    PromptThreatType.TOOL_POLICY_BYPASS,
    PromptThreatType.DATA_EXFILTRATION,
}
WARN_KEYWORDS = (
    'red team autorizado', 'authorized red team', 'prueba de seguridad', 'security test',
    'no destructiva', 'non destructive', 'non-destructive', 'malware', 'laboratorio', 'lab',
)


class PromptPolicy:
    def decide(self, text: str, matches: list[PromptThreatMatch], context=None) -> PromptSecurityDecision:
        threats = [m.threat_type for m in matches if m.threat_type != PromptThreatType.BENIGN]
        patterns = [m.pattern_name for m in matches if m.threat_type != PromptThreatType.BENIGN]
        lowered = (text or '').lower()
        if any(threat in BLOCK_THREATS for threat in threats):
            return PromptSecurityDecision(
                risk_level=PromptRiskLevel.BLOCK,
                threats=threats,
                reason='prompt_security_blocked_policy_or_secret_bypass',
                matched_patterns=patterns,
                safe_to_call_llm=False,
            )
        if any(threat in {PromptThreatType.IGNORE_PREVIOUS_INSTRUCTIONS, PromptThreatType.ROLEPLAY_BYPASS, PromptThreatType.INSTRUCTION_OVERRIDE} for threat in threats):
            return PromptSecurityDecision(
                risk_level=PromptRiskLevel.BLOCK,
                threats=threats,
                reason='prompt_security_blocked_instruction_override',
                matched_patterns=patterns,
                safe_to_call_llm=False,
            )
        if any(keyword in lowered for keyword in WARN_KEYWORDS):
            risk = PromptRiskLevel.ESCALATE_TO_POLICY if any(word in lowered for word in ('red team', 'malware')) else PromptRiskLevel.WARN
            return PromptSecurityDecision(
                risk_level=risk,
                threats=[PromptThreatType.UNSAFE_AUTONOMY_REQUEST] if risk == PromptRiskLevel.ESCALATE_TO_POLICY else [],
                reason='prompt_security_warn_dual_use_or_lab_context',
                matched_patterns=patterns,
                safe_to_call_llm=True,
            )
        return PromptSecurityDecision(
            risk_level=PromptRiskLevel.ALLOW,
            threats=[PromptThreatType.BENIGN],
            reason='prompt_security_allow_benign',
            matched_patterns=[],
            safe_to_call_llm=True,
        )
