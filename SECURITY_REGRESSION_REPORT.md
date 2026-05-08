# SECURITY REGRESSION REPORT

## Phase 6B-3 Telegram Real Gated Security Status
Date: 2026-05-07

## Security Controls

### Token Handling
- `TELEGRAM_BOT_TOKEN` is loaded from environment/config only.
- Real mode refuses startup without token.
- Token is redacted from `TelegramConfig.__repr__`, gateway logs, evidence, and message outputs.
- `.env.example` documents variables without real values.

### Allowlist
- `TELEGRAM_ALLOWED_USER_IDS` is required for real mode.
- Empty allowlist fails closed in real mode.
- Unauthorized users receive `DENIED`.

### Rate Limiting
- Gateway/operator use per-user rate limiting.
- `TELEGRAM_RATE_LIMIT_PER_MINUTE` is supported.

### Replay Protection and Approvals
- ApprovalWorkflow creates unique approval IDs.
- ApprovalWorkflow hashes the action payload.
- Approval fails on replayed action hash.
- Approval fails on action hash mismatch.
- R4 requires approval.
- R5 is blocked.

### Sandbox and Evidence
- Mission dispatch goes through `SandboxDispatcher` and `SandboxController`.
- R5 never dispatches.
- EvidenceLogger records incoming message, authorization, policy, approval, mission, and sandbox events with redaction.

### Secret Scan
- No real secrets found.
- Scan output contains expected variable names, code redaction patterns, and historical/test fixtures only.

### Legacy Telegram Scan
- No active `saga_fusion/telegram_mission_operator/` runtime directory.
- No active imports to the legacy path found in `saga_fusion/telegram`.
- Historical reports still mention the removed legacy path for audit traceability.

## Verdict
Security regression status: PASS for Phase 6B-3 gated real Telegram preflight.


## Security Regression Report (Phase 6B-4)
- LLM enabled flag defaults to false.
- LLM endpoint/model/API key are env-only.
- API key is redacted in repr.
- Unit tests do not call real LLM endpoint.
- LLM failures fall back safely and do not break TelegramGateway.
- BrainService does not execute tools and cannot bypass MissionPolicy, ApprovalWorkflow, or SandboxController.
- Real mission execution remains disabled/not performed.


## Security Regression Report (Phase 6B-4B)
- Spanish/English destructive actions normalize to R5 and are blocked.
- Spanish/English infrastructure-changing actions normalize to R4 and require approval.
- Mixed intent uses highest-risk-wins semantics.
- Smoke confirmed no real action execution for R4/R5 probes.
- Secret literal scan found 0 runtime token/API-key leaks in reports/source/tests.
