# PHASE 10F-2 — Telegram Main Engine Wiring Report

## Summary
Telegram lab runtime now sends full free-form Telegram messages into the STRIX natural-language mission path first. Saga Fusion remains the control layer around that path: authorization, rate limiting, PromptSecurity, MissionPolicy/DangerousActionPolicy, TaskPlanner, ToolRouter, ApprovalVerifier, SandboxController dry-run dispatch, evidence logging, report-pack generation when compatible, and redaction.

## Primary wiring
- Telegram transport: `saga_fusion/telegram/telegram_lab_runtime.py`
  - Polls Bot API, redacts responses, and calls `TelegramMissionOperator.handle_message(chat_id, user_id, text)` with the full user message.
- STRIX main-engine entrypoint for Telegram: `saga_fusion/telegram/mission_operator.py`
  - `handle_message()` keeps Telegram auth/rate/control gates, then calls `_handle_main_engine_message()` for natural language.
  - `_handle_main_engine_message()` runs PromptSecurity, `LLMRouter.build_mission_from_natural_language()` (deterministic fallback when LLM disabled), `TaskPlanner`, `MissionPolicy`, `ToolRouter`, approval generation for R4, and `SandboxDispatcher`/`SandboxController` dry-run for allowed non-blocked paths.
- Saga Fusion control layer: `saga_fusion/telegram/mission_operator.py`
  - Existing policy/approval/sandbox/evidence/report/redaction components remain in the mission operator and are not bypassed.

## Defensive router status
`DefensiveCommandRouter` is no longer the primary Telegram path for natural language. It is only used for:
1. explicit lab/control defensive slash commands such as `/defense_status`; or
2. temporary fallback when `main_engine_available` is false or the main path raises and the defensive router can handle the text.

Fallback responses are marked with:
- `routed_by=defensive_command_router_fallback`
- `strix_main_engine_primary=false`

Main-engine responses are marked with:
- `routed_by=strix_main_engine`
- `strix_main_engine_primary=true`
- `saga_control_layer=true`

## Natural-language coverage added
`PatternRegistry` now recognizes natural Telegram phrasing for:
- `que puedes hacer`
- `revisa el estado del sistema`
- `analiza si esto parece phishing`
- `quiero revisar procesos raros`

Defensive workflow report packs are built on the main path when the workflow plan satisfies the report-pack safety contract. Generic workflow plans remain evidence/report-only and do not force incompatible report-pack construction.

## Persistent service
Persistent safe lab poller already exists and remains:
- service file: `deploy/systemd/strix-telegram-lab.service`
- command: `python3 -m saga_fusion.telegram.telegram_lab_runtime --service --poll-timeout-seconds 15 --start-at-latest`

The service uses polling with webhook disabled and acknowledges handled offsets to avoid duplicate pollers/replies.

## Validation
Executed:

```bash
python3 -m pytest tests/telegram tests/defensive_workflows tests/reporting -q
# 119 passed

python3 -m pytest tests -q
# 436 passed, 3 warnings
```

Warnings are existing coroutine warnings in STRIX/Saga integration/security tests and are not caused by this Telegram wiring change.

## Live Telegram
Preflight completed without exposing secrets:

```json
{"ok": true, "mode": "real", "polling_enabled": true, "webhook_enabled": false, "allowed_user_count": 1, "bot_username": "RadamanthysCyberBot", "token": "[REDACTED]"}
```

Live message test was not completed because no real user messages were available in this background execution. Attempting to ask the parent for live messages failed because `DUCTOR_TASK_ID` was not set in this execution context. No live result is claimed.

## Safety
- No real LLM calls were required by tests; LLMRouter uses deterministic fallback unless explicitly enabled.
- No Bot API token or secret was printed.
- R4 remains approval-required; R5 remains blocked.
- `advanced_authorized` behavior was not globally capped or modified.
- PromptSecurity, MissionPolicy, DangerousActionPolicy, ApprovalVerifier, SandboxController, ToolRouter, manifests, report redaction, and report-pack contracts were preserved.
- No Agent Zero/OpenCLAW/Hermes/Qwen/TurboQuant/llama.cpp files were changed.
