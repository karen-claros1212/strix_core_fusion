from __future__ import annotations

from .tool_registry import ToolRegistry
from .tool_routing_types import ToolCategory, ToolRisk
from ..policy import DangerousActionCategory, DangerousActionPolicy

READ_VERBS = ('status','list','show','get','read','leer','lista','muestra','revisa logs')
AUDIT_VERBS = ('audit','audita','scan','escanea','review','revisa','dry-run','dry run')
CREATE_VERBS = ('create','crear','provision','provisionar','deploy','desplegar','abrir puerto','cambia el dns')
DELETE_VERBS = ('delete','destroy','wipe','elimina','borra','destruye')


class ToolClassifier:
    def __init__(self, registry: ToolRegistry | None = None):
        self.registry = registry or ToolRegistry()
        self.dangerous_action_policy = DangerousActionPolicy()

    def classify(self, request, context=None) -> dict:
        text = self._request_text(request)
        explicit = self._explicit_tool(request)
        dangerous = self.dangerous_action_policy.evaluate(text)
        if dangerous.blocked:
            return {
                'tool_name': explicit or 'cloudops_plan',
                'category': ToolCategory.CLOUDOPS,
                'risk_level': ToolRisk.R5,
                'matched': dangerous.reason,
                'dangerous_action': dangerous,
            }
        if dangerous.approval_required:
            category = ToolCategory.CLOUDOPS
            if DangerousActionCategory.FIREWALL_EXPOSURE in dangerous.categories:
                category = ToolCategory.NETWORK
            return {
                'tool_name': explicit or 'cloudops_plan',
                'category': category,
                'risk_level': ToolRisk.R4,
                'matched': dangerous.reason,
                'dangerous_action': dangerous,
            }
        if explicit and self.registry.exists(explicit):
            tool = self.registry.get(explicit)
            return {'tool_name': tool.name, 'category': tool.category, 'risk_level': tool.default_risk, 'matched': 'explicit_tool'}
        lowered = text.lower()
        if any(v in lowered for v in DELETE_VERBS):
            return {'tool_name': explicit or 'cloudops_plan', 'category': ToolCategory.CLOUDOPS, 'risk_level': ToolRisk.R5, 'matched': 'destructive_verb'}
        if any(v in lowered for v in CREATE_VERBS) or 'vps' in lowered:
            return {'tool_name': explicit or 'cloudops_plan', 'category': ToolCategory.CLOUDOPS, 'risk_level': ToolRisk.R4, 'matched': 'infra_change'}
        if 'secret' in lowered or 'secreto' in lowered:
            return {'tool_name': 'secret_scan', 'category': ToolCategory.REPO_AUDIT, 'risk_level': ToolRisk.R2, 'matched': 'secret_scan'}
        if 'dependency' in lowered or 'dependenc' in lowered:
            return {'tool_name': 'dependency_audit', 'category': ToolCategory.REPO_AUDIT, 'risk_level': ToolRisk.R2, 'matched': 'dependency_audit'}
        if 'docker' in lowered or 'compose' in lowered:
            return {'tool_name': 'docker_audit', 'category': ToolCategory.REPO_AUDIT, 'risk_level': ToolRisk.R2, 'matched': 'docker_audit'}
        if any(v in lowered for v in AUDIT_VERBS):
            return {'tool_name': 'repo_audit', 'category': ToolCategory.REPO_AUDIT, 'risk_level': ToolRisk.R3, 'matched': 'repo_audit'}
        if any(v in lowered for v in READ_VERBS):
            return {'tool_name': 'status', 'category': ToolCategory.READ_ONLY, 'risk_level': ToolRisk.R0, 'matched': 'read_only'}
        if explicit:
            return {'tool_name': explicit, 'category': ToolCategory.UNKNOWN, 'risk_level': ToolRisk.R4, 'matched': 'unknown_explicit'}
        return {'tool_name': 'unknown', 'category': ToolCategory.UNKNOWN, 'risk_level': ToolRisk.R4, 'matched': 'unknown'}

    def _request_text(self, request) -> str:
        if isinstance(request, dict):
            parts = [request.get('tool_name',''), request.get('action',''), request.get('target',''), request.get('arguments',''), request.get('raw_text','')]
        else:
            parts = [getattr(request,'tool_name',''), getattr(request,'action_type',''), getattr(request,'target',''), getattr(request,'arguments',''), getattr(request,'raw_text','')]
        return ' '.join(str(p or '') for p in parts)

    def _explicit_tool(self, request) -> str:
        if isinstance(request, dict):
            return str(request.get('tool_name') or '').strip().lower()
        return str(getattr(request, 'tool_name', '') or '').strip().lower()
