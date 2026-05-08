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


## Risk Register Update (Phase 6C-1)
- [OPEN] RB-6C1-01: Static dry-run repo audit found findings requiring triage before production-grade 6C expansion.
- [CLOSED] RB-6C1-02: Repository audit evidence could leak secrets; mitigated with redaction and literal secret scan.


## Risk Register Update (Phase 6C-2)
- [OPEN] RB-6C2-01: Repo audit scanner false positives can create alert fatigue and obscure real future findings. Priority P2.
- [ACCEPTED] RB-6C2-02: Historical reports and synthetic test fixtures intentionally contain secret-like strings; keep with labels/allowlists. Priority P3.


## Risk Register Update (Phase 6C-3)
- [CLOSED] RB-6C2-01 partial: Auto-fix-safe scanner false positives for `.env.example` placeholders and test config fixtures reduced.
- [OPEN] RB-6C3-01: Manual-review findings remain for redaction code self-hits, historical report labeling, and synthetic secret fixtures. Target: Phase 6C-4.


## Risk Register Update (Phase 6C-4)
- [OPEN] RB-6C4-01: Redaction-code self-hit requires targeted scanner classification patch in 6C-5. Risk: LOW alert fatigue.
- [ACCEPTED] RB-6C4-02: Synthetic secret-like test fixtures remain for redaction coverage. Risk: INFO scanner noise.
- [DOCUMENTATION] RB-6C4-03: Historical report placeholders should be labeled/preserved, not deleted. Risk: INFO documentation drift.


## Risk Register Update (Phase 6C-5)
- [CLOSED] RB-6C4-01: Redaction-code self-hit now classifies as `scanner_self_reference` INFO, not HIGH secret leak.
- [MONITORED] RB-6C4-02: Synthetic fixtures remain accepted and are classified as INFO fixture evidence.
- [MONITORED] RB-6C4-03: Historical report placeholders remain preserved and are classified as INFO historical evidence.


## Risk Register Update (Phase 6C-6)
- [CLOSED] RB-6C1-01: Repository audit findings triaged/remediated/classified through 6C final re-audit.
- [CLOSED] RB-6C4-01: Redaction self-reference classification regression resolved.
- [ACCEPTED] RB-6C4-02: Synthetic fixtures remain monitored accepted risk.
- [DOCUMENTATION] RB-6C4-03: Historical evidence placeholders preserved for audit traceability.
- [READY] Phase 7 CAI patterns may begin under controlled/lab constraints.


## Risk Register Update (Phase 7A)
- [OPEN] RB-7A-01: CAI-inspired tool routing could bypass STRIX gates if implemented directly. Mitigation: clean-room reimplementation under MissionPolicy/ApprovalWorkflow/SandboxController only.
- [OPEN] RB-7A-02: Offensive/recon/exploit workflows are dual-use. Mitigation: documentation/pattern extraction only until explicit authorized lab phase.
- [OPEN] RB-7A-03: Prompt patterns may carry prompt-injection risk. Mitigation: adapt hardening lessons, never copy prompts as trusted instructions.


## Risk Register Update (Phase 7B)
- [OPEN] RB-7B-01: Tool routing implementation could bypass SandboxController if built before prompt/policy gates. Mitigation: implement prompt security first in 7C.
- [OPEN] RB-7B-02: CAI pattern extraction can drift into runtime compatibility. Mitigation: clean-room Saga Fusion modules only.
- [OPEN] RB-7B-03: Future offensive/recon patterns require explicit authorized lab scope before any execution capability.


## Risk Register Update (Phase 7C)
- [CLOSED] RB-7B-01 partial: Prompt security now precedes LLM routing, reducing risk before future tool routing.
- [OPEN] RB-7C-01: Pattern-based prompt detection may miss novel prompt injection variants. Mitigation: expand detector regression corpus as evidence grows.
- [OPEN] RB-7C-02: 7D tool routing must consume prompt-security metadata without bypassing MissionPolicy/SandboxController.


## Risk Register Update (Phase 7D)
- [CLOSED] RB-7B-01: Tool routing is now subordinate to MissionPolicy and SandboxController metadata, with no direct execution path.
- [OPEN] RB-7D-01: Dangerous-action taxonomy needs further hardening and broader ES/EN coverage in 7E.
- [OPEN] RB-7D-02: Future tool integrations must not convert ToolExecutionPlan into execution outside SandboxController.
