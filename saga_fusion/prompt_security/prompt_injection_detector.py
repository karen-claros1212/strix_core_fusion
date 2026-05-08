from __future__ import annotations

import re
from dataclasses import dataclass

from .prompt_security_types import PromptThreatType


@dataclass(frozen=True)
class PromptThreatMatch:
    threat_type: PromptThreatType
    pattern_name: str
    matched_text: str


class PromptInjectionDetector:
    def __init__(self):
        self.patterns: list[tuple[PromptThreatType, str, re.Pattern]] = [
            (PromptThreatType.IGNORE_PREVIOUS_INSTRUCTIONS, 'ignore_previous_en', re.compile(r'(?i)\b(ignore|disregard|forget)\s+(all\s+)?(previous|prior)\s+(instructions|rules)\b')),
            (PromptThreatType.IGNORE_PREVIOUS_INSTRUCTIONS, 'ignore_previous_es', re.compile(r'(?i)\b(ignora|olvida|omite)\s+(las\s+)?(instrucciones|reglas)\s+(anteriores|previas)\b')),
            (PromptThreatType.SYSTEM_PROMPT_EXFILTRATION, 'system_prompt_en', re.compile(r'(?i)\b(show|tell|reveal|print|dump)\b.*\b(system prompt|developer message|initial instructions)\b')),
            (PromptThreatType.SYSTEM_PROMPT_EXFILTRATION, 'system_prompt_es', re.compile(r'(?i)\b(dime|muestra|revela|imprime)\b.*\b(system prompt|prompt del sistema|instrucciones internas)\b')),
            (PromptThreatType.SECRET_EXFILTRATION, 'env_file', re.compile(r'(?i)\b(read|cat|show|lee|muestra|env[ií]a)\b.*(\.env|environment variables|variables de entorno|~/\.ssh|ssh key|clave ssh)')),
            (PromptThreatType.SECRET_EXFILTRATION, 'reveal_secrets', re.compile(r'(?i)\b(reveal|exfiltrate|send|dump|filtra|exfiltra|env[ií]a)\b.*\b(secret|secrets|token|tokens|api key|api_key|password|contraseñas?|credenciales)\b')),
            (PromptThreatType.TOOL_POLICY_BYPASS, 'mission_policy_bypass', re.compile(r'(?i)\b(bypass|omite|ignora|skip|disable|desactiva|no uses?)\b.*\b(MissionPolicy|policy|pol[ií]tica|R4|R5|approval|aprobaci[oó]n|SandboxController|sandbox|evidence|evidencia)\b')),
            (PromptThreatType.TOOL_POLICY_BYPASS, 'execute_without_approval', re.compile(r'(?i)\b(ejecuta|execute|run)\b.*\b(sin aprobaci[oó]n|without approval|no approval)\b')),
            (PromptThreatType.TOOL_POLICY_BYPASS, 'no_evidence', re.compile(r'(?i)\b(no|do not|dont|don\'t)\b.*\b(registres? evidencia|log evidence|record evidence|evidence logging)\b')),
            (PromptThreatType.ROLEPLAY_BYPASS, 'unrestricted_mode', re.compile(r'(?i)\b(act[uú]a como|pretend|roleplay|modo)\b.*\b(sin restricciones|unrestricted|developer mode|modo libre|jailbreak)\b')),
            (PromptThreatType.INSTRUCTION_OVERRIDE, 'instruction_override', re.compile(r'(?i)\b(new instructions|override instructions|reemplaza instrucciones|nuevas instrucciones|act[uú]a ahora como)\b')),
            (PromptThreatType.DATA_EXFILTRATION, 'hidden_exfil', re.compile(r'(?i)\b(hazlo|do it)\b.*\b(sin que el usuario lo sepa|without the user knowing|silently exfiltrate|en secreto)\b')),
            (PromptThreatType.UNSAFE_AUTONOMY_REQUEST, 'unsafe_autonomy', re.compile(r'(?i)\b(autonomous|aut[oó]nomo|sin supervisi[oó]n|sin confirmaci[oó]n|without confirmation)\b.*\b(execute|ejecuta|deploy|delete|borra|elimina)\b')),
        ]

    def detect(self, text: str) -> list[PromptThreatMatch]:
        value = text or ''
        matches: list[PromptThreatMatch] = []
        for threat_type, name, pattern in self.patterns:
            match = pattern.search(value)
            if match:
                matches.append(PromptThreatMatch(threat_type, name, match.group(0)))
        if not matches:
            matches.append(PromptThreatMatch(PromptThreatType.BENIGN, 'benign', ''))
        return matches
