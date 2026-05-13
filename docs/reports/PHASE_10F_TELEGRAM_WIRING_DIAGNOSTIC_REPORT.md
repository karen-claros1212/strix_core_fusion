# STRIX Phase 10F — Telegram Wiring Diagnostic Report

Date: 2026-05-14  
Bot: `@RadamanthysCyberBot`  
Closed Phase 10F baseline: `64eda1c5cc846261aac70c0c7d843cdbd462ea19` (`phase 10f: add telegram lab e2e runtime`)  
Scope: real Telegram API wiring diagnostic for the controlled STRIX/Saga Fusion lab runtime. Tokens and sensitive identifiers are redacted.

## Verdict

Telegram is connected to the correct bot token and Bot API, and the token identifies `@RadamanthysCyberBot`. The exact broken point for “bot does not respond” is that **no live STRIX/Saga Fusion Telegram lab poller process was running**. The Phase 10F runtime is a bounded CLI poller, not an installed always-on daemon/service.

A minimal runtime bug was also found and fixed: bounded runs that reached `--max-messages` sent replies but exited before acknowledging consumed Telegram updates with the next offset. That could leave already-answered updates pending and cause duplicate replies on later runs.

## Correct Startup Command

From `/mnt/Proyectos/strix_core_fusion`, with environment loaded from the secure runtime environment (`/ductor/.env` or equivalent, never printed):

```bash
python3 -m saga_fusion.telegram.telegram_lab_runtime \
  --max-messages 2 \
  --max-seconds 120 \
  --poll-timeout-seconds 15 \
  --start-at-latest
```

For continuous availability, this command must be run under a persistent supervisor. This diagnostic did not modify `/ductor/.env` or `/ductor/config/config.json`.

## Process Check

Result: no live Python process running `saga_fusion.telegram.telegram_lab_runtime` was found outside the diagnostic command itself.

```text
live_telegram_lab_runtime_process=false
```

## Token / Bot Identity

`getMe` succeeded using the env-only token without printing the token.

```text
ok=True
username=RadamanthysCyberBot
bot_id=...2057
is_bot=True
```

Conclusion: the loaded token corresponds to `@RadamanthysCyberBot`.

## Webhook Status

`getWebhookInfo` showed polling-compatible state:

```text
ok=True
webhook_url_set=False
pending_update_count=0
allowed_updates=["message"]
last_error_set=False
```

No webhook deletion was needed.

## Direct `getUpdates` Diagnostic

Current direct `getUpdates` check, redacted:

```text
ok=True
conflict_409=False
updates_count=0
updates=[]
```

Earlier in this diagnostic, Telegram had queued two pending messages for this bot:

```text
ok=True
conflict_409=False
updates_count=2
updates:
- update_id=459705044, from_id=...3211, chat_id=...3211, text="Hola", authorized=True
- update_id=459705045, from_id=...3211, chat_id=...3211, text="Hola", authorized=True
```

Conclusion: Telegram delivery to the bot works and the observed sender was allowlisted. The failure was not token, webhook, chat allowlist, or Telegram delivery. The failure was absence of a running STRIX poller.

## Runtime Response Test

A controlled bounded runtime run was launched against the pending `Hola` updates:

```bash
python3 -m saga_fusion.telegram.telegram_lab_runtime --max-messages 2 --max-seconds 30 --poll-timeout-seconds 5
```

Result after the acknowledgement fix:

```text
status=ok
messages_handled=2
send_ok=True for both updates
ack_ok=True
acknowledged_offset=459705046
```

A later fresh-message polling window was also run:

```bash
python3 -m saga_fusion.telegram.telegram_lab_runtime --max-messages 2 --max-seconds 60 --poll-timeout-seconds 10 --start-at-latest
```

Result:

```text
preflight_ok=True
messages_handled=0
status=timeout
```

No fresh target messages arrived during that window, so the requested live target-command smoke remains incomplete.

## Receives / Responds / Conflict Summary

```text
telegram_connected=True
webhook_disabled_for_polling=True
allowlist_configured=True
observed_sender_authorized=True
409_conflict=False
receives_messages=True for queued Telegram messages observed during diagnostic
responds_when_runtime_started=True for queued messages consumed by runtime
target_commands_received_fresh=False during latest bounded polling window
target_command_live_response_complete=False
```

## Defensive Path Verification

Unit/fake Bot API tests verify the intended defensive route for requested lab commands:

```text
telegram_lab_runtime.py
-> TelegramMissionOperator.handle_message
-> defensive_command_router.py
-> defensive_commands.py natural-language mapping
-> defensive workflow/status payload
-> sendMessage
```

Verified cases:

- `revisa un adjunto sospechoso en modo seguro` routes to `phishing_attachment` with lab-mode report-pack output and safety flags.
- `estado defensa` routes to `defense_status` with available workflows and lab-mode safety flags.

## Allowlist Status

```text
configured_allowed_user_count=1
observed_sender=...3211
authorized=True
```

Sensitive IDs are redacted.

## Fix Applied

Files changed:

- `saga_fusion/telegram/telegram_lab_runtime.py`
  - Added final zero-timeout `getUpdates(offset=<next_offset>)` acknowledgement after a bounded run handles messages.
  - Added redacted evidence event: `telegram_lab_ack`.
- `tests/telegram/test_telegram_lab_runtime.py`
  - Added regression coverage that handled updates are acknowledged before bounded exit.
- `docs/reports/PHASE_10F_TELEGRAM_WIRING_DIAGNOSTIC_REPORT.md`
  - Added exact wiring diagnostic evidence and startup command.

No `.env` or `/ductor/config/config.json` changes were made.

## Tests

```bash
python3 -m pytest tests/telegram tests/defensive_workflows tests/reporting -q
# 114 passed

python3 -m pytest tests -q
# 431 passed, 3 existing warnings
```

Warnings are existing coroutine-not-awaited warnings in integration/security tests.

## Safety

- No token or secret printed.
- No `.env` or `/ductor/config/config.json` modification.
- No real LLM invocation.
- No CloudOps, malware, payloads, webshells, attachments, or destructive execution.
- Telegram use was lab/evidence-only.
- R4/R5 controls and lab safety flags were not weakened.
- Old untracked Phase 6B-4 reports/logs were not staged.

## Next Action

Run the startup command under a persistent supervisor, then send fresh messages to `@RadamanthysCyberBot` during the polling window:

1. `revisa un adjunto sospechoso en modo seguro`
2. `estado defensa`

Expected: live `send_ok=True` for both, with `phishing_attachment` and `defense_status` responses respectively.

## Commit / Push Status

A local diagnostic/fix commit exists on `main` and includes only the Phase 10F runtime acknowledgement fix, regression test, and this report. Push status is recorded in the final task response because the commit hash may change if the report is amended.
