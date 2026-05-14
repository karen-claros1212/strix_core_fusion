# Phase 10F-5 Natural-First STRIX Telegram Report

## STRIX Core Verification — Exact Command Output

```text
=== pip show strix-agent ===
WARNING: Package(s) not found: strix-agent
=== import StrixAgent ===
Traceback (most recent call last):
  File "<string>", line 1, in <module>
ImportError: cannot import name 'StrixAgent' from 'strix.agents' (unknown location)
=== ls strix/agents ===
__pycache__
base_agent.py
state.py
unified_saga_agent.py
=== pyproject grep strix ===
```

## Classification
GAP DETECTED.

- `strix-agent==0.8.3` is not installed in this runtime.
- `from strix.agents import StrixAgent` fails.
- The fork currently contains local `strix/agents` stubs/placeholders (`base_agent.py`, `state.py`, `unified_saga_agent.py`) rather than the official importable `StrixAgent` package.

Recommended fix: install `strix-agent==0.8.3` in the runtime or vendor the official source under the approved STRIX Core boundary, then rerun the exact verification commands before claiming real STRIX Core availability.

## Before
Telegram UX was command-oriented in several paths:
- legacy `/mission ...` tests represented mission UX;
- defensive workflows had slash commands such as `/malware_triage`, `/ransomware_response`, `/phishing_review`, `/webshell_investigation`;
- unknown slash commands could produce command errors.

## After
Telegram UX is natural-first:
- Free text never requires `/mission`.
- Free text is sent to the canonical STRIX Telegram gateway first.
- If `StrixCoreGateway.is_available() == False`, the existing Saga Fusion/LLMRouter path is used as fallback.
- If STRIX Core is available, LLMRouter fallback is not used.
- Unknown free text does not produce `Unknown command`.

## Slash Commands
Visible slash command surface is limited to admin/debug:
- `/status`
- `/help`
- `/approve`
- `/deny`
- `/report`

`/help` response:

```text
Escríbeme en lenguaje natural. Ejemplos:
 revisa estado del sistema, analiza posible ransomware,
 audita repo, genera reporte defensivo.
```

## Defensive Workflows by Natural Language
Covered examples:
- `analiza posible ransomware` -> ransomware response workflow
- `haz triage defensivo de malware` -> malware triage workflow
- `revisa posible webshell` -> webshell investigation workflow

## Fallback Condition
Fallback to the Saga Fusion/LLMRouter path is allowed only when the STRIX gateway reports unavailable via `is_available() == False` or when the main engine is unavailable and a legacy safe fallback explicitly handles the request.

## Security Preservation
- `crea un VPS en Hostinger` -> R4 `approval_required`.
- `elimina servidor y borra backups` -> R5 `blocked`.
- `execution_allowed=False` remains enforced in lab/fallback outputs.
- `executed=False` remains enforced unless a separately approved/sandboxed flow explicitly allows execution.
- No tokens or `.env` files were touched.
- No real Telegram/LLM/CloudOps/pentest/malware/payload/webshell/attachment/destructive action was executed by tests.

## Validation
- `python3 -m pytest tests/telegram -q --tb=short` -> `97 passed`
- `python3 -m pytest tests/telegram tests/defensive_workflows tests/brain -q --tb=short` -> `149 passed`
- `python3 -m pytest tests -q --tb=short` -> `476 passed, 3 warnings`

## Verdict
Code/test status: GO for live natural-first Telegram smoke.

Blocking gap for real STRIX Core claim: official `strix-agent==0.8.3` / `StrixAgent` is not installed/importable in this runtime.
