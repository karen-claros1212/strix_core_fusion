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


## Risk Register Update (Phase 7E)
- [CLOSED] RB-7D-01: Dangerous-action taxonomy now covers filesystem destruction, secrets/exfiltration, infra deletion, backup deletion, firewall exposure, and bypass attempts.
- [OPEN] RB-7E-01: R4 approval metadata should be hardened next so sensitive allowed plans carry complete HITL context. Target: 7F.
- [OPEN] RB-7E-02: Read-only secret audit scope remains intentionally blocked until explicit scope semantics are implemented.


## Risk Register Update (Phase 7F)
- [CLOSED] RB-7E-01: R4 approvals now include approval_id, action_hash, expiry, evidence_ref, and authorized-user verification.
- [OPEN] RB-7F-01: Future execution adapters must enforce ApprovalVerifier + SandboxController before approved R4 dispatch. Target: later execution phases.
- [OPEN] RB-7F-02: Reporting should expose approval evidence and denial reasons without leaking secrets. Target: 7G.

## Risk Register Update (Phase 7G)
- [CLOSED] RB-7F-02: Reporting now exposes approval/evidence context through redacted structured reports and Telegram-safe summaries.
- [OPEN] RB-7G-01: Future report exporters must preserve ReportRedactor and OutputBudget behavior for every new format.
- [OPEN] RB-7G-02: Task planner/pattern registry should produce reportable execution intent without bypassing MissionPolicy or ToolRouter. Target: 7H.


## Risk Register Update (Phase 7H)
- [CLOSED] RB-7G-02: Task planner/pattern registry now emits reportable execution intent without bypassing MissionPolicy or ToolRouter.
- [OPEN] RB-7H-01: Future planners must not convert ExecutionIntent into execution outside SandboxController and ApprovalVerifier.
- [OPEN] RB-7H-02: Defensive workflow templates should reuse PatternRegistry without widening scope to external pentest or CloudOps real execution. Target: 7I.

## Risk Register Update (Phase 7I)
- [CLOSED] RB-7H-02: Defensive workflow templates now reuse PatternRegistry/TaskPlanner without widening scope to external pentest or CloudOps real execution.
- [OPEN] RB-7I-01: Future workflow adapters must not convert `WorkflowPlan` into automatic remediation; mitigation is mandatory `execution_allowed=False`, ApprovalVerifier/SandboxController gating, and tests.
- [OPEN] RB-7I-02: Offline dependency vulnerability review is placeholder-only; future online checks require explicit scope, network policy, evidence redaction, and approval.
- [READY] Phase 7J can add memory/context patterns while preserving PromptSecurity, MissionPolicy, DangerousActionPolicy, ToolRouter, ApprovalVerifier, SandboxController, EvidenceLogger, and Reporting authority.

## Risk Register Update (Phase 7J)
- [CLOSED] RB-7I-02 partial: Memory/context patterns now preserve policy authority and block raw secret storage before future Hermes-pattern work.
- [OPEN] RB-7J-01: Regex-only secret detection may miss novel secret formats. Mitigation: continue adding redaction regression fixtures and keep `SECRET_BLOCKED` conservative.
- [OPEN] RB-7J-02: Retrieval is lexical/process-local only. Future durable or semantic memory must preserve redaction, `SECRET_BLOCKED` exclusion, and non-authoritative policy guarantees.
- [READY] Phase 8 Hermes Patterns can proceed only as clean-room pattern adaptation with no Hermes runtime/code copy and with PromptSecurity/MissionPolicy authority unchanged.


## Risk Register Update (Phase 8A)
- [OPEN] RB-8A-01: Hermes-inspired gateway/toolset patterns could duplicate STRIX Telegram/ToolRouter paths if implemented directly. Mitigation: no Hermes runtime or gateway integration; clean-room design only.
- [OPEN] RB-8A-02: Skill/plugin patterns can import untrusted instructions or side effects. Mitigation: future STRIX extension governance must keep plugins docs-only or sandbox-gated with PromptSecurity and ApprovalVerifier.
- [OPEN] RB-8A-03: Cron/long-running task patterns can repeat sensitive actions or stall on approvals. Mitigation: future jobs must be dry-run by default, scoped, bounded, redacted, and evidence-backed.
- [OPEN] RB-8A-04: Context compression/recovery can drop safety constraints. Mitigation: never compress away system policy, R4/R5 rules, redaction rules, or evidence requirements.
- [READY] Phase 8B may proceed as Hermes pattern design only; no runtime compatibility layer, gateway, terminal backend, self-improvement loop, or real external execution.

<!-- PHASE_8A_BIS_RISKS -->
## Phase 8A-BIS — Hermes Pattern Risks
| risk_id | risk | severity | status | mitigation |
|---|---|---:|---|---|
| 8A-BIS-R1 | Accidentally staging `external_sources/hermes-agent` or vendoring Hermes code. | HIGH | Mitigated | Added/kept `external_sources/` in `.gitignore`; verify `git status --short --ignored`. |
| 8A-BIS-R2 | Importing Hermes plugins/skills could bypass STRIX policy. | HIGH | Open for future phases | Documentation-only; any implementation must be clean-room and disabled by default. |
| 8A-BIS-R3 | Scheduled tasks can execute stale/destructive instructions. | HIGH | Open for 8D | Begin with dry-run scheduled audit specs and SandboxController gating. |
| 8A-BIS-R4 | Memory/context compaction can promote untrusted text to instructions. | MEDIUM | Open for 8C | Non-authoritative summary template, context fences, scrubber tests, policy precedence. |
| 8A-BIS-R5 | Gateway/session recovery can route approvals or reports to wrong recipient. | HIGH | Open for 8D | Redacted session IDs, task-local context, delivery manifests, restart-drain tests. |

<!-- PHASE_8B_REV_RISKS -->
## Phase 8B-REV — Hermes Pattern Design Risks
| risk_id | risk | severity | status | mitigation |
|---|---|---|---|---|
| 8B-REV-R1 | Metadata/plugin governance could become runtime plugin loading by accident. | HIGH | Open for 8C | 8C must remain schema/docs-first, disabled by default, no dynamic import. |
| 8B-REV-R2 | Toolset scoping could create a parallel Hermes-like tool path. | HIGH | Open for 8D | ToolRouter/ApprovalVerifier/SandboxController remain mandatory; no Hermes toolset. |
| 8B-REV-R3 | Dry-run scheduler could drift into unattended execution. | HIGH | Open for 8E | Dry-run specs only; owner/timezone/budget/evidence required; no OS cron/live actions. |
| 8B-REV-R4 | Recovery/compression could route approvals incorrectly or promote untrusted summary text. | HIGH | Open for 8F | Session ownership checks; non-authoritative summaries; preserve R4/R5/redaction invariants. |
| 8B-REV-R5 | LLM error recovery could hide auth/billing or leak data via fallback. | MEDIUM | Open for 8H | Reporting-first taxonomy; no credential rotation or unapproved provider fallback. |
| 8B-REV-R6 | Approval timeout semantics could weaken into allow-always. | HIGH | Open for 8I | Timeout-to-deny only; R5 non-approvable; exact action hash/user/channel/session checks. |
| READY | Phase 8C may proceed only with explicit approval and without Hermes runtime/code copy. | INFO | Ready | Use the 8B-REV backlog and acceptance criteria. |

## Risk Register Update (Phase 8C)
- [CLOSED] RB-8C-01: Skill/plugin metadata could bypass STRIX tool policy. Mitigation: ToolRouter blocks tools outside manifest `allowed_tools` when skill context is present.
- [CLOSED] RB-8C-02: Skill metadata could request direct secrets. Mitigation: validator/policy reject dangerous permissions and direct secret request metadata; required_env is name-only.
- [CLOSED] RB-8C-03: Skill metadata could weaken R4/R5 controls. Mitigation: R4 requires approval, R5 blocked, unknown/disabled blocked.
- [MONITORED] RB-8C-04: Future skill execution would expand attack surface. Current status: no execution path; any future execution must remain behind MissionPolicy, ApprovalVerifier, and SandboxController.

## Risk Register Update (Phase 8D)
- [CLOSED] RB-8D-01: Toolset scoping could create a parallel Hermes-like execution path. Mitigation: `ScopedToolRouter` wraps existing `ToolRouter` only and introduces no execution; `SandboxController` remains the boundary.
- [CLOSED] RB-8D-02: Skills could widen their own tool scope. Mitigation: `ToolScopePolicy` blocks requested skill scopes that exceed the manifest `allowed_tools` set.
- [CLOSED] RB-8D-03: Tool-routing loops could repeat or recurse indefinitely. Mitigation: `ToolLoopGuard` enforces per-mission max calls, repeated same tool+args limits, and active-stack recursion blocking.
- [MONITORED] RB-8D-04: Future scheduler/cron work could bypass these scopes. Mitigation: Phase 8E must consume scoped-router/loop-guard semantics and remain dry-run/spec-only.
- [READY] Phase 8E can proceed only with explicit approval and without OS cron/live actions or unattended execution.

## Risk Register Update (Phase 8E)
- [CLOSED] RB-8D-04 / 8B-REV-R3: Scheduler/cron patterns could drift into unattended execution. Mitigation: Phase 8E is metadata/planning only; `execution_allowed=False`, mandatory dry-run, no execute/run method, no OS cron, and no workspace cron_tools scheduling.
- [CLOSED] RB-8E-01: Scheduled R4/R5 actions could bypass approval/blocking. Mitigation: R4 jobs are approval-required metadata; R5/destructive jobs are blocked and non-approvable.
- [CLOSED] RB-8E-02: Scheduled-job evidence could leak secrets. Mitigation: evidence refs, arguments, and metadata are redacted for token/password/API-key/Authorization-like values.
- [MONITORED] RB-8E-03: Future session recovery/context compression could revive blocked or stale scheduler metadata. Mitigation: Phase 8F must preserve non-authoritative recovery summaries, cancellation status, R4/R5 gates, redaction, and `execution_allowed=False` invariants.
- [READY] Phase 8F can proceed only with explicit approval and without weakening scheduler, approval, redaction, or SandboxController boundaries.

## Risk Register Update (Phase 8F)
- [CLOSED] RB-8F-01: Recovered or compressed context could be treated as authoritative instructions. Mitigation: `CompressedContext` and snapshot policy metadata force non-authoritative/non-executable handling and prompt builder renders it as user-context-only background.
- [CLOSED] RB-8F-02: Snapshot tampering or stale recovery could restore unsafe state. Mitigation: canonical checksum verification and expiry rejection.
- [CLOSED] RB-8F-03: Secret-bearing context could leak through session summaries. Mitigation: `MemoryRedactor` reuse, secret-bearing context exclusion, and redacted intent markers.
- [CLOSED] RB-8F-04: Recovered context could downgrade R4/R5 policy. Mitigation: highest-risk-wins enforcement; MissionPolicy, PromptSecurity, and SandboxController remain authoritative.
- [READY] Phase 8G Evidence / Reporting Manifests may begin.

## Risk Register Update (Phase 8G)
- [CLOSED] RB-8G-01: Evidence/report artifacts could be untraceable or tampered after generation. Mitigation: manifest refs require SHA-256 and validator detects mismatches for existing local paths.
- [CLOSED] RB-8G-02: Reporting manifests could leak raw secret-bearing artifact content. Mitigation: manifests store references/hashes/metadata only, block raw content/body metadata keys, and reuse ReportRedactor.
- [CLOSED] RB-8G-03: Manifest metadata could be treated as executable instructions. Mitigation: manifest refs and manifests enforce `non_authoritative=True`, `execution_allowed=False`, and expose no execution surface.
- [READY] Phase 8H LLM Error Taxonomy + Recovery may begin with reporting-first, bounded recovery semantics and no hidden credential/provider fallback.

## Risk Register Update (Phase 8H)
- [CLOSED] 8B-REV-R5 / RB-8H-01: LLM recovery could hide auth/billing failures. Mitigation: auth is classified critical, nonretryable, redacted, and surfaced in `llm_recovery` metadata with safe fallback.
- [CLOSED] RB-8H-02: LLM retry logic could loop indefinitely. Mitigation: `LLMRecoveryPolicy.max_retry_count` and category caps bound all retries; max exhaustion stops and falls back.
- [CLOSED] RB-8H-03: Fallback could leak secrets or downgrade safety. Mitigation: evidence redaction covers API keys/Bearer tokens and fallback uses deterministic non-executing router under MissionPolicy/action normalization.
- [CLOSED] RB-8H-04: Unsafe LLM output could bypass PromptSecurity/MissionPolicy/SandboxController. Mitigation: unsafe-output classification triggers safe fallback and preserves existing authorities.
- [READY] Phase 8I Approval Timeout + Regression Depth may begin with timeout-to-deny semantics and deeper approval/session regression coverage.

## Risk Register Update (Phase 8I)
- [CLOSED] 8B-REV-R6 / RB-8I-01: Approval timeout semantics could weaken into allow-always. Mitigation: approvals expire at/after TTL and expiry is terminal/non-executing.
- [CLOSED] RB-8I-02: Approval replay could reuse a HITL grant. Mitigation: used approvals become `USED` and verifier blocks replay with explicit evidence.
- [CLOSED] RB-8I-03: Hash mismatch or wrong actor could approve a different action. Mitigation: exact action hash and allowlisted actor checks are deterministic; mismatches are terminal and unauthorized actors are blocked.
- [CLOSED] RB-8I-04: R5 or nonexistent approvals could be approved through command paths. Mitigation: R5 missions create no approval, R5 approval attempts are blocked, and missing IDs are blocked.
- [READY] Phase 9 original STRIX optimization or Phase 8 closure may proceed with SandboxController, R4 HITL approval, R5 non-approvable blocking, and no direct execution unchanged.


## Risk Register Update (Phase 9C)
- [CLOSED] RB-9C-01: Policy optimization could downgrade R5/R4 decisions. Mitigation: golden policy evaluation tests passed and dangerous-action decision semantics remained unchanged.
- [CLOSED] RB-9C-02: Faster tool classification/scoping could skip unknown-tool or scope gates. Mitigation: targeted policy/security/approval/telegram suite passed and ToolScopePolicy remains non-executing.
- [CLOSED] RB-9C-03: Optimization could weaken approvals, redaction, manifest, or sandbox boundaries. Mitigation: full first-party suite passed and no runtime capability or config changes were introduced.
- [READY] Phase 9D planning may proceed only as planning. Further policy optimization requires new profiling and golden coverage.

## Risk Register Update (Phase 10A)
- [CLOSED] RB-10A-01: STRIX lacked a native defensive cyber knowledge package for malware taxonomy, ATT&CK mapping, detection-rule templates, IoC reports, and playbook references. Mitigation: added `saga_fusion/cyber_knowledge/` with non-executing builders and tests.
- [OPEN] RB-10A-02: Detection content remains template-level and non-authoritative. Mitigation: reports and rules label defensive/non-authoritative status; Phase 10B may add curated defensive workflows with additional validation.
- [ENFORCED] RB-10A-03: Malware execution, payload creation, persistence, exfiltration, and bypass functionality remain blocked by scope and builder validation.

## Risk Register Update (Phase 10B)
- [CLOSED] RB-10A-01 partial: Cyber knowledge is now used by advanced defensive workflows without adding malware execution or offensive capability.
- [OPEN] RB-10B-01: Future lab/Telegram commands could accidentally convert workflow recommendations into actions. Mitigation: keep `execution_allowed=False`, ToolRouter non-executing, ApprovalVerifier/SandboxController gates, and add command-level lab-mode regressions in Phase 10C.
- [MONITORED] RB-10B-02: Detection templates are non-authoritative and require analyst validation to avoid false positives.
- [READY] Phase 10C can add defensive Telegram commands / lab mode only if these workflows remain plan/report/evidence only by default.
