# STRIX RISK REGISTER - SECURITY VULNERABILITIES

## 1. Context Management Risks
- **Risk:** Memory overflow due to unbounded conversation history.
- **Mitigation:** `SagaContextManager` with soft/hard limits and summarization.

## 2. Tool Execution Risks
- **Risk:** Command injection via LLM-generated actions.
- **Mitigation:** `SagaSecurityPolicy`, `SandboxController`, and dry-run default dispatch.

## 3. Credential Leakage
- **Risk:** API keys, Telegram tokens, or bearer tokens exposed in logs/outputs.
- **Mitigation:** Env-only token loading, safe config repr, TelegramSecurity redaction, EvidenceLogger redaction, and output budgeting.

## 4. Sandbox Escape
- **Risk:** Tools breaking out of the execution environment.
- **Mitigation:** Strict sandbox policy, filesystem/network/resource guards, and mandatory `SandboxController` dispatch.

## 5. Telegram Real Mode Misconfiguration
- **Risk:** Real Telegram gateway starts without token or allowlist.
- **Status:** CLOSED in Phase 6B-3.
- **Mitigation:** `validate_real_mode_config()` blocks real mode unless both `TELEGRAM_BOT_TOKEN` and `TELEGRAM_ALLOWED_USER_IDS` are present.

## 6. Unauthorized Telegram Users
- **Risk:** Unknown Telegram user triggers STRIX/Saga actions.
- **Status:** CLOSED in Phase 6B-3.
- **Mitigation:** Fail-closed allowlist validation and `DENIED` response.

## 7. Approval Replay / Tampering
- **Risk:** Approval callback reused or action payload changed after approval request.
- **Status:** CLOSED in Phase 6B-3.
- **Mitigation:** Approval action hashes, replay guard, and hash mismatch rejection.

## Current Phase 6B-3 Verdict
- `RB-6B3-01`: Real Telegram connection pending gated token test — READY FOR CONTROLLED TOKEN TEST.
- `RB-6B3-02`: Mock mode regression — CLOSED, tests green.
- `RB-6B3-03`: R4/R5 policy regression — CLOSED, tests green.


## Risk Register Update (Phase 6B-4B)
- [CLOSED] RB-6B4B-01: Spanish natural-language R4/R5 intents were not deterministically canonicalized before MissionPolicy.
- Mitigation: ES/EN canonical action normalizer with highest-risk-wins behavior, covered by tests and real Telegram smoke.
