from __future__ import annotations

from typing import Iterable

from saga_fusion.cyber_knowledge import (
    IncidentPlaybookRegistry,
    IoC,
    MitreMapper,
    SigmaRuleBuilder,
    ThreatClassification,
    YaraRuleBuilder,
    infer_ioc_type,
)
from saga_fusion.cyber_knowledge.threat_types import ThreatCategory

from .defensive_workflow_types import DefensiveCommandSuggestion, DefensiveWorkflowPlan, make_workflow_id, redact_obj


def iocs(values: Iterable[str], source: str = "reported") -> list[dict]:
    out = []
    for value in values or []:
        text = str(value or "").strip()
        if text:
            out.append(IoC(text, infer_ioc_type(text), source=source, confidence=0.55).to_dict())
    return redact_obj(out)


def mitre(behaviors: Iterable[str]) -> list[dict]:
    return [item.to_dict() for item in MitreMapper().map_behaviors(behaviors)]


def playbook(playbook_id: str) -> dict | None:
    p = IncidentPlaybookRegistry().get(playbook_id)
    if not p:
        return None
    payload = p.to_dict()
    payload["execution_allowed"] = False
    return payload


def yara(name: str, strings: list[str], description: str) -> list[dict]:
    try:
        return [YaraRuleBuilder().build_rule(name, strings, description=description, tags=("defensive", "strix_phase_10b")).to_dict()]
    except Exception as exc:  # defensive builders may reject unsafe text
        return [{"name": name, "error": str(exc), "execution_allowed": False, "defensive_only": True}]


def sigma(title: str, detection: dict, description: str, level: str = "medium", tags=("attack.defense_evasion",)) -> list[dict]:
    try:
        rule = SigmaRuleBuilder().build_rule(
            title,
            {"product": "windows", "category": "process_creation"},
            detection,
            description=description,
            level=level,
            tags=tuple(tags),
        )
        return [rule.to_dict()]
    except Exception as exc:
        return [{"name": title, "error": str(exc), "execution_allowed": False, "defensive_only": True}]


def classification(category: ThreatCategory | str, confidence: float, summary: str, matched_terms: tuple[str, ...] = ()) -> dict:
    cat = category if isinstance(category, ThreatCategory) else ThreatCategory(str(category)) if str(category) in {c.value for c in ThreatCategory} else ThreatCategory.UNKNOWN
    return ThreatClassification(cat, confidence, matched_terms=matched_terms, defensive_summary=summary, execution_allowed=False, metadata={"phase": "10b", "defensive_only": True}).to_dict()


def cmd(command: str, purpose: str) -> DefensiveCommandSuggestion:
    return DefensiveCommandSuggestion(command=command, purpose=purpose, read_only=True, dry_run=True, execution_allowed=False)


def build_plan(prefix: str, title: str, summary: str, **kwargs) -> DefensiveWorkflowPlan:
    return DefensiveWorkflowPlan(workflow_id=make_workflow_id(prefix), title=title, summary=summary, metadata={"phase": "10b", "toolrouter_executes": False, **kwargs.pop("metadata", {})}, **kwargs)
