# STRIX Phase 10F — Telegram Lab E2E Real Report

Date: 2026-05-13  
Base: `d051ff4d58be1711419bb21c0a0772ed32ee5a6c` (`phase 10e: add local e2e smoke coverage`)  
Scope: controlled real Telegram lab transport for defensive/evidence-only workflows.

## Objective
Validate the controlled path:

`Telegram message -> TelegramLabRuntime polling -> TelegramMissionOperator -> DefensiveCommandRouter -> lab policy envelope -> defensive workflow -> DefensiveReportPack refs -> Telegram response`

## Files Modified
- `saga_fusion/telegram/telegram_lab_runtime.py` — new real Telegram polling runtime for controlled lab E2E with redacted preflight, Bot API `getMe` preflight, `getUpdates` polling, and `sendMessage` response handling.
- `saga_fusion/telegram/defensive_commands.py` — maps natural-language `estado defensa` to the defensive status/capabilities response.
- `saga_fusion/telegram/defensive_command_router.py` — adds DefensiveReportPack references (`pack_id`, `evidence_refs`, `report_refs`, `manifest_refs`) to lab Telegram workflow responses.
- `tests/telegram/test_telegram_lab_runtime.py` — fake Bot API tests; no real Telegram calls.
- `tests/telegram/test_defensive_command_router.py` — verifies report-pack refs in Telegram defensive routing.
- `tests/telegram/test_defensive_commands.py` — verifies `estado defensa` natural-language mapping.

## Secure Runtime Configuration
Required environment variables for live lab mode:

```text
TELEGRAM_BOT_TOKEN=[REDACTED]
TELEGRAM_ALLOWED_USER_IDS=[REDACTED_ALLOWED_USER_IDS]
TELEGRAM_MODE=real
TELEGRAM_POLLING_ENABLED=true
TELEGRAM_WEBHOOK_ENABLED=false
TELEGRAM_RATE_LIMIT_PER_MINUTE=10
```

Notes:
- Token is loaded from env/secure runtime config only.
- Token is never hardcoded, printed, committed, or stored in docs.
- Unit tests use fake/injected API clients and do not call real Telegram.
- No `.env` or `/ductor/config/config.json` changes were made.

## How to Start Bot in Lab Mode
From `/mnt/Proyectos/strix_core_fusion`, with the env vars above present:

```bash
python3 -m saga_fusion.telegram.telegram_lab_runtime \
  --max-messages 2 \
  --max-seconds 120 \
  --poll-timeout-seconds 15 \
  --start-at-latest
```

Then send these exact messages from an allowlisted Telegram user to `@RadamanthysCyberBot`:

1. `revisa un adjunto sospechoso en modo seguro`
2. `estado defensa`

`--start-at-latest` ignores old backlog and waits for fresh lab messages.

## Expected Live Case Behavior
### Case 1: `revisa un adjunto sospechoso en modo seguro`
Expected route: `phishing_attachment`.

Expected response properties:
- `status=workflow_plan`
- `workflow_category=phishing_attachment`
- `pack_id` starts with `defensive-pack-`
- `evidence_refs`, `report_refs`, `manifest_refs` present
- `execution_allowed=False`
- `executed=False`
- `non_authoritative=True`
- `evidence_required=True`
- `report_required=True`
- no attachment processing or execution

### Case 2: `estado defensa`
Expected route: `defense_status`.

Expected response properties:
- `status=ok`
- `workflow_category=defense_status`
- available defensive workflows/capabilities returned
- `execution_allowed=False`
- `executed=False`
- `non_authoritative=True`
- `evidence_required=True`
- `report_required=True`

## Live Lab Smoke Result
Preflight was available and passed with redacted output:

```text
ok=True
mode=real
polling_enabled=True
webhook_enabled=False
allowed_user_count=1
bot_username=RadamanthysCyberBot
token=[REDACTED]
```

A controlled polling run was attempted:

```bash
python3 -m saga_fusion.telegram.telegram_lab_runtime --max-messages 2 --max-seconds 30 --poll-timeout-seconds 5 --start-at-latest
```

Result:

```text
status=timeout
messages_handled=0
evidence=[]
preflight.ok=True
```

Verdict for live smoke: **NO-GO / incomplete**, because no fresh allowlisted Telegram messages were received during the bounded polling window. No live result was fabricated.

## Tests
```bash
python3 -m pytest tests/telegram tests/defensive_workflows tests/reporting -q
# 113 passed

python3 -m pytest tests -q
# 430 passed, 3 existing warnings
```

Warnings are the pre-existing coroutine-not-awaited warnings in integration/security tests.

## Safety Checks
- Real Telegram is only used by the explicit lab runtime after preflight.
- Unit tests never call Telegram real APIs.
- Defensive workflow responses remain evidence/report-only.
- `execution_allowed=False`, `executed=False`, `non_authoritative=True`, `evidence_required=True`, `report_required=True` are preserved.
- No malware execution.
- No attachment execution or processing.
- No payload/webshell generation.
- No destructive commands.
- No external pentest/CloudOps.
- No real LLM.
- No Qwen/TurboQuant/llama.cpp changes.
- No Agent Zero/OpenCLAW/Hermes changes.
- No `.env` or `/ductor/config/config.json` changes.
- No R4/R5, PromptSecurity, MissionPolicy, SandboxController, approval flow, manifest validation, or redaction weakening.
- Old untracked Phase 6B-4 reports/logs remained unstaged.

## Git Diff Stat Before Commit
```text
saga_fusion/telegram/defensive_command_router.py | 5 +++++
saga_fusion/telegram/defensive_commands.py       | 3 +++
saga_fusion/telegram/telegram_lab_runtime.py     | 259 ++++++++++++++++++++++++
tests/telegram/test_defensive_command_router.py  | 2 ++
tests/telegram/test_defensive_commands.py        | 1 +
tests/telegram/test_telegram_lab_runtime.py      | 109 ++++++++++
```

## Verdict
Code/tests/report: **GO**.  
Live Telegram smoke evidence: **NO-GO / incomplete until the allowlisted user sends the two required messages during polling**.

## Commit / Push Status
Local commit created:

```text
7ee76002b165c045976cfb6882c83ec07ab3456b phase 10f: add telegram lab e2e runtime
```

Push attempt:

```text
git push origin main
fatal: could not read Username for 'https://github.com': No such device or address
```

Local-vs-origin after failed push:

```text
ahead=1
behind=0
```

Remote closure remains pending until GitHub HTTPS credentials are available or the commit is pushed from the host.
