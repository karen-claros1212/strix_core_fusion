# STRIX ELITE CYBER AGENT - Project Synopsis

## Purpose
STRIX Elite Cyber Agent is the single STRIX core with Saga Fusion as the owned security, sandbox, evidence, Telegram, and CloudOps layer.

## Current Root
`/mnt/Proyectos/strix_core_fusion`

## Phase Status
- Phase 0+1: baseline/documentation
- Phase 2/2.5: Saga Fusion over real STRIX
- Phase 3/3.5: tests/regression
- Phase 4: Evidence Store + Output Budget + Runtime Safety
- Phase 5: CloudOps / InfraOps Operator
- Phase 6B-2: Telegram mock mode completed
- Phase 6B-3: gated real Telegram integration completed
- Current full suite: 141 passed, 3 warnings

## Architecture
- `strix/`: STRIX core; not modified in Phase 6B-3
- `saga_fusion/`: owned Saga Fusion layer
- `saga_fusion/runtime/sandbox/`: mandatory sandbox runtime
- `saga_fusion/telegram/`: official Telegram interface
- `saga_fusion/evidence/`: evidence capture

## Telegram Phase 6B-3 Summary
- Real mode is gated by env/config and refuses startup when required settings are missing.
- Mock mode remains intact and requires no token.
- Real token is env-only via `TELEGRAM_BOT_TOKEN`.
- Allowed users are required for real mode via `TELEGRAM_ALLOWED_USER_IDS`.
- Rate limiting, replay protection, approval hashes, R4 approvals, R5 blocking, evidence logging, and output/secret redaction are active.
- Tests use mock/injected clients and do not call Telegram real APIs.

## Core Rules
- STRIX is the only core.
- Telegram is an interface, not a separate project.
- R4 requires approval.
- R5 is blocked.
- Nothing executes outside `SandboxController`.
- No real secrets in repository.


## Phase 6B-4 LLM Brain Gateway
- Added `saga_fusion/llm/` as the local brain gateway for OpenAI-compatible Qwen/TurboQuant/llama.cpp endpoints.
- LLM is disabled by default via `STRIX_LLM_ENABLED=false`.
- Endpoint/model/API key are env-driven; code has no hardcoded LLM endpoint or key.
- Natural Telegram messages may be structured by the brain only when enabled, then still pass through MissionPolicy, ApprovalWorkflow, SandboxController, and EvidenceLogger.
- Unit tests mock the LLM and never call the real endpoint.


## Phase 6B-4B Canonical ES/EN Action Normalization
- Added deterministic ES/EN mission action normalization before risk classification.
- Destructive intents such as `elimina servidor` and `borra backups` canonicalize to `delete` and become R5 blocked.
- Infrastructure-changing intents such as `crea VPS`, `cambia DNS`, `abre puerto`, and `restaura backup` canonicalize to R4 approval-required actions.
- Highest risk wins when benign/R4 and destructive terms appear together.
