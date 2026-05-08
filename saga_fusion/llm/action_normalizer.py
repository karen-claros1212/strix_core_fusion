import re
import unicodedata

R5_PATTERNS = [
    r"\brm\s+-rf\b",
    r"\b(delete|destroy|wipe|remove|erase)\b",
    r"\b(elimina|eliminar|elimine|destruye|destruir|borra|borrar|wipea|remueve|remover)\b",
    r"\b(borra|borrar|elimina|eliminar)\b.*\bbackup(s)?\b",
    r"\b(elimina|eliminar|destruye|destruir|borra|borrar)\b.*\b(servidor|server|vps|instancia)\b",
]

R4_PATTERNS = [
    r"\b(create|deploy|(?<!dry-)run|execute|provision|open|change|restore)\b",
    r"\b(crea|crear|cree|provisiona|provisionar|despliega|desplegar|ejecuta|ejecutar)\b",
    r"\b(cambia|cambiar|modifica|modificar)\b.*\bdns\b",
    r"\b(abre|abrir|expon|exponer)\b.*\b(puerto|port)\b",
    r"\b(restaura|restaurar|restore)\b.*\bbackup(s)?\b",
]

R3_PATTERNS = [
    r"\b(scan|audit|backup|collect|report)\b",
    r"\b(auditoria|auditar|revisa|revisar|analiza|analizar|dry-run|dry run|informe|reporte)\b",
]

R0_PATTERNS = [
    r"\b(status|show|list|get|health|estado)\b",
    r"\b(revisa|revisar)\b.*\bestado\b",
]


def normalize_text(text: object) -> str:
    raw = "" if text is None else str(text)
    decomposed = unicodedata.normalize("NFKD", raw.lower())
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def _matches(patterns: list[str], text: str) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def canonicalize_action(*parts: object) -> str:
    text = normalize_text(" ".join(str(part) for part in parts if part is not None))
    # Highest risk wins. Destructive intent overrides any create/audit/status terms.
    if _matches(R5_PATTERNS, text):
        return "delete"
    if _matches(R4_PATTERNS, text):
        return "create"
    if _matches(R0_PATTERNS, text):
        return "status"
    if _matches(R3_PATTERNS, text):
        return "scan"
    return "status" if not text.strip() else text.split(maxsplit=1)[0]


def canonicalize_mission(action_type: object = "", target: object = "", arguments: object = "", raw_text: object = "") -> dict:
    action = canonicalize_action(action_type, target, arguments, raw_text)
    clean_target = "" if target is None else str(target).strip()
    clean_arguments = "" if arguments is None else str(arguments).strip()
    raw = "" if raw_text is None else str(raw_text).strip()
    if raw and not clean_target:
        raw_parts = raw.split(maxsplit=1)
        raw_first = canonicalize_action(raw_parts[0]) if raw_parts else ""
        if raw_first == action and len(raw_parts) > 1:
            clean_target = raw_parts[1]
        else:
            clean_target = raw
    if not clean_arguments:
        clean_arguments = clean_target
    return {
        "action_type": action,
        "target": clean_target,
        "arguments": clean_arguments,
    }
