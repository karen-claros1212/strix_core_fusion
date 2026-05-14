# STRIX Phase 10F-2 — Telegram Persistent Lab Service Report

Date: 2026-05-14  
Bot: `@RadamanthysCyberBot`  
Base diagnostic closure: `8a9a888fede6230a3196aa1e44f67144535c0a3c` (`phase 10f: fix telegram lab wiring`)  
Scope: persistent polling service for the real Telegram lab transport, preserving STRIX/Saga Fusion evidence-only safety constraints.

## Verdict

Implemented a persistent lab-mode Telegram poller for STRIX/Saga Fusion.

The bounded runtime remains available for tests and smoke windows. The new `--service` mode runs continuously without requiring `--max-messages` or `--max-seconds`, polls Telegram, routes allowlisted messages through the existing lab pipeline, sends Telegram responses, immediately acknowledges handled update offsets, and logs only redacted operational status.

No persistent service was installed or left running from this task.

## Runtime Commands

### Persistent lab service mode

```bash
python3 -m saga_fusion.telegram.telegram_lab_runtime \
  --service \
  --poll-timeout-seconds 15 \
  --start-at-latest
```

`--service` ignores bounded `--max-messages` and `--max-seconds` values.

### Bounded smoke mode

```bash
python3 -m saga_fusion.telegram.telegram_lab_runtime \
  --max-messages 2 \
  --max-seconds 120 \
  --poll-timeout-seconds 15 \
  --start-at-latest
```

## Systemd User Service

Service unit added:

```text
deploy/systemd/strix-telegram-lab.service
```

Documentation added:

```text
docs/deploy/STRIX_TELEGRAM_LAB_SERVICE.md
```

Install/start commands for a user service:

```bash
mkdir -p ~/.config/systemd/user
cp deploy/systemd/strix-telegram-lab.service ~/.config/systemd/user/strix-telegram-lab.service
systemctl --user daemon-reload
systemctl --user enable --now strix-telegram-lab.service
systemctl --user status strix-telegram-lab.service --no-pager
journalctl --user -u strix-telegram-lab.service -n 50 --no-pager
```

The unit uses `EnvironmentFile=%h/.ductor/.env`; it does not contain secrets.

Key service properties:

```text
WorkingDirectory=/mnt/Proyectos/strix_core_fusion
ExecStart=/usr/bin/python3 -m saga_fusion.telegram.telegram_lab_runtime --service --poll-timeout-seconds 15 --start-at-latest
Restart=on-failure
TELEGRAM_MODE=real
TELEGRAM_POLLING_ENABLED=true
TELEGRAM_WEBHOOK_ENABLED=false
```

## Duplicate Poller Check

Container process checks were limited because standard `pgrep`/`ps` are unavailable in this image. A `/proc` command-line scan found no active Python `saga_fusion.telegram.telegram_lab_runtime` process before bounded live testing.

```text
live_telegram_lab_runtime_process=false
```

No persistent poller was left running.

## Implementation Summary

Changed files:

- `saga_fusion/telegram/telegram_lab_runtime.py`
  - Added `--service` CLI option.
  - Added `TelegramLabRuntime.run_service(...)` for continuous polling.
  - Preserved bounded `run(...)` behavior.
  - Added service startup/poll logging with secret redaction.
  - Acknowledges handled Telegram offsets during service mode to reduce duplicate update processing across restarts.
  - Returns non-zero from CLI service mode when preflight is `no_go`, allowing `Restart=on-failure` to handle startup failures.
- `tests/telegram/test_telegram_lab_runtime.py`
  - Added service-mode argument parsing coverage.
  - Added fake Bot API service-loop coverage with update acknowledgement and lab safety assertions.
- `deploy/systemd/strix-telegram-lab.service`
  - User systemd service template with env-only secrets and `Restart=on-failure`.
- `docs/deploy/STRIX_TELEGRAM_LAB_SERVICE.md`
  - Installation/start/status/log commands and safety notes.

## Safety Controls Preserved

- Token loaded from env only; no hardcoded/stored token.
- Polling mode only; webhook disabled in the service environment.
- Allowlist remains required by `TelegramSecurity` / `TelegramMissionOperator`.
- Telegram responses are produced through existing STRIX/Saga Fusion lab pipeline.
- Logs and report evidence redact token/user-sensitive values.
- No real LLM call.
- No CloudOps.
- No external pentest.
- No malware, payload, webshell, attachment execution, or destructive command.
- R4/R5 controls, PromptSecurity, MissionPolicy, SandboxController, approval flow, manifests, report/evidence requirements, and redaction were not weakened.
- Lab/evidence-only flags remain asserted in tests and runtime evidence: `execution_allowed=False`, `executed=False`, `non_authoritative=True`, `evidence_required=True`, `report_required=True`.

## Fake Bot API Tests

Service-mode tests use only a fake Bot API and do not call real Telegram.

Validated behavior:

- `--service` parses without requiring bounded max values.
- Service loop polls repeatedly with `max_polls` test guard.
- Allowlisted `estado defensa` is routed to `defense_status`.
- Response and evidence preserve lab safety flags.
- Handled update is acknowledged with `getUpdates(offset=<next_offset>, timeout=0)`.
- Token is not present in serialized result output.

## Real Telegram Smoke

A bounded live Telegram smoke was attempted; no persistent service was left running.

### Attempt 1

Command:

```bash
python3 -m saga_fusion.telegram.telegram_lab_runtime \
  --max-messages 2 \
  --max-seconds 45 \
  --poll-timeout-seconds 5 \
  --start-at-latest
```

Redacted result summary:

```text
preflight.ok=True
bot_username=RadamanthysCyberBot
allowed_user_count=1
status=timeout
messages_handled=1
request_text="Stado defensa"
send_ok=True
ack_ok=True
execution_allowed=False
executed=False
non_authoritative=True
evidence_required=True
report_required=True
```

This proved live Telegram receive/respond still works, but it did **not** validate the requested `estado defensa` path because the received text was `Stado defensa`.

### Attempt 2

Command:

```bash
python3 -m saga_fusion.telegram.telegram_lab_runtime \
  --max-messages 2 \
  --max-seconds 60 \
  --poll-timeout-seconds 5 \
  --start-at-latest
```

Redacted result summary:

```text
preflight.ok=True
bot_username=RadamanthysCyberBot
allowed_user_count=1
status=timeout
messages_handled=0
evidence=[]
```

Requested target messages were not received during the second bounded window:

1. `estado defensa`
2. `revisa un adjunto sospechoso en modo seguro`

No live target-command result was fabricated.

## Validation

```bash
python3 -m pytest tests/telegram tests/defensive_workflows tests/reporting -q
# 116 passed

python3 -m pytest tests -q
# 433 passed, 3 existing warnings
```

Warnings are the pre-existing coroutine-not-awaited warnings in integration/security tests.

## Git / Push Status

Commit and push status are recorded in the final task response after commit/push attempt. Old untracked Phase 6B-4 reports/logs were intentionally left unstaged.
