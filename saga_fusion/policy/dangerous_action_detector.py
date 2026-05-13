from __future__ import annotations

import re
from dataclasses import dataclass

from .dangerous_action_types import DangerousActionCategory, DangerousActionSeverity


@dataclass(frozen=True)
class DangerousActionMatch:
    category: DangerousActionCategory
    severity: DangerousActionSeverity
    pattern_name: str
    matched_text: str


class DangerousActionDetector:
    def __init__(self):
        self.patterns: list[tuple[DangerousActionCategory, DangerousActionSeverity, str, re.Pattern]] = [
            (DangerousActionCategory.DESTRUCTIVE_FILESYSTEM, DangerousActionSeverity.CRITICAL, 'rm_rf', re.compile(r'(?i)\brm\s+-rf\b|\brm\s+-fr\b')),
            (DangerousActionCategory.DESTRUCTIVE_FILESYSTEM, DangerousActionSeverity.CRITICAL, 'wipe_format_shred', re.compile(r'(?i)\b(wipe|format|shred|delete all|borrar todo|eliminar archivos)\b')),
            (DangerousActionCategory.CREDENTIAL_EXFILTRATION, DangerousActionSeverity.CRITICAL, 'secret_exfil', re.compile(r'(?i)(env[ií]a|send|upload|curl|exfiltrate|leak|filtra|exfiltra).*(secret|token|password|credential|credencial|\.env|~/.ssh|private key)')),
            (DangerousActionCategory.CREDENTIAL_EXFILTRATION, DangerousActionSeverity.CRITICAL, 'secret_read_and_send', re.compile(r'(?i)(lee|read|cat|muestra|show).*(\.env|~/.ssh|private key|token|password|credentials?).*(env[ií]a|send|upload|exfiltrate|leak|filtra|exfiltra)')),
            (DangerousActionCategory.SECRET_ACCESS, DangerousActionSeverity.HIGH, 'secret_access', re.compile(r'(?i)(lee|read|cat|muestra|show).*(\.env|~/.ssh|private key|token|password|credentials?)')),
            (DangerousActionCategory.INFRASTRUCTURE_DESTRUCTION, DangerousActionSeverity.CRITICAL, 'infra_destroy', re.compile(r'(?i)(elimina|borra|destruye|delete|destroy|terminate).*(servidor|server|vps|droplet|instance|instancia)')),
            (DangerousActionCategory.CLOUD_RESOURCE_DELETION, DangerousActionSeverity.CRITICAL, 'cloud_delete', re.compile(r'(?i)(delete|destroy|terminate|elimina|borra).*(cloud|resource|recurso|instancia|instance)')),
            (DangerousActionCategory.BACKUP_DELETION, DangerousActionSeverity.CRITICAL, 'backup_delete', re.compile(r'(?i)(borra|elimina|delete|wipe|remove).*(backup|backups|snapshot|snapshots|restore point|punto de restauraci[oó]n)')),
            (DangerousActionCategory.FIREWALL_EXPOSURE, DangerousActionSeverity.CRITICAL, 'disable_firewall', re.compile(r'(?i)(disable|desactiva|apaga).*(firewall|ufw|iptables)')),
            (DangerousActionCategory.FIREWALL_EXPOSURE, DangerousActionSeverity.HIGH, 'expose_ssh', re.compile(r'(?i)(abre|open|expose|allow).*(ssh|puerto\s*22|port\s*22).*(0\.0\.0\.0/0|p[uú]blico|public|all inbound)')),
            (DangerousActionCategory.FIREWALL_EXPOSURE, DangerousActionSeverity.CRITICAL, 'allow_all_inbound', re.compile(r'(?i)(allow all inbound|permitir todo entrante|0\.0\.0\.0/0.*all|all.*0\.0\.0\.0/0)')),
            (DangerousActionCategory.CLOUD_RESOURCE_CREATION, DangerousActionSeverity.HIGH, 'cloud_create', re.compile(r'(?i)(create|crear|provision|provisionar|deploy|desplegar).*(vps|server|servidor|instance|instancia|cloud)')),
            (DangerousActionCategory.POLICY_BYPASS, DangerousActionSeverity.CRITICAL, 'mission_policy_bypass', re.compile(r'(?i)(omite|ignora|bypass|skip|disable|desactiva|no uses?).*(MissionPolicy|pol[ií]tica|approval|aprobaci[oó]n|R4|R5)')),
            (DangerousActionCategory.SANDBOX_BYPASS, DangerousActionSeverity.CRITICAL, 'sandbox_bypass', re.compile(r'(?i)(bypass|omite|ignora|skip|disable|desactiva|no uses?).*(sandbox|SandboxController)')),
            (DangerousActionCategory.EVIDENCE_SUPPRESSION, DangerousActionSeverity.CRITICAL, 'evidence_suppression', re.compile(r'(?i)(no|do not|dont|don\'t|disable|desactiva).*(registr(es|ar)? evidencia|evidence|logs?|logging)')),
            (DangerousActionCategory.PRIVILEGE_ESCALATION, DangerousActionSeverity.CRITICAL, 'privilege_escalation', re.compile(r'(?i)(privilege escalation|escalar privilegios|sudo su|root shell|setuid)')),
        ]
        self._prefilter_terms: dict[str, tuple[str, ...]] = {
            'rm_rf': ('rm',),
            'wipe_format_shred': ('wipe', 'format', 'shred', 'delete all', 'borrar todo', 'eliminar archivos'),
            'secret_exfil': ('envía', 'envia', 'send', 'upload', 'curl', 'exfiltrate', 'leak', 'filtra', 'exfiltra'),
            'secret_read_and_send': ('lee', 'read', 'cat', 'muestra', 'show'),
            'secret_access': ('lee', 'read', 'cat', 'muestra', 'show'),
            'infra_destroy': ('elimina', 'borra', 'destruye', 'delete', 'destroy', 'terminate'),
            'cloud_delete': ('delete', 'destroy', 'terminate', 'elimina', 'borra'),
            'backup_delete': ('borra', 'elimina', 'delete', 'wipe', 'remove'),
            'disable_firewall': ('disable', 'desactiva', 'apaga'),
            'expose_ssh': ('abre', 'open', 'expose', 'allow'),
            'allow_all_inbound': ('allow all inbound', 'permitir todo entrante', '0.0.0.0/0'),
            'cloud_create': ('create', 'crear', 'provision', 'provisionar', 'deploy', 'desplegar'),
            'mission_policy_bypass': ('omite', 'ignora', 'bypass', 'skip', 'disable', 'desactiva', 'no use'),
            'sandbox_bypass': ('bypass', 'omite', 'ignora', 'skip', 'disable', 'desactiva', 'no use'),
            'evidence_suppression': ('no', 'do not', 'dont', "don't", 'disable', 'desactiva'),
            'privilege_escalation': ('privilege escalation', 'escalar privilegios', 'sudo su', 'root shell', 'setuid'),
        }

    def detect(self, text: str) -> list[DangerousActionMatch]:
        value = text or ''
        matches=[]
        lowered = value.lower()
        prefilter_terms_by_name = self._prefilter_terms
        for category, severity, name, pattern in self.patterns:
            if not any(term in lowered for term in prefilter_terms_by_name[name]):
                continue
            match = pattern.search(value)
            if match:
                matches.append(DangerousActionMatch(category, severity, name, match.group(0)))
        return matches
