# Phase 8B-REV — Hermes Pattern Implementation Design Reconciliation

Status: COMPLETE — design/documentation reconciliation only.

## Scope and source baseline
- Previous STRIX baseline: Phase 8A-BIS, commit `8dd2638` on `main`, full suite `250 passed / 0 failed / 3 warnings`.
- Hermes source audit baseline: read-only checkout at ignored `external_sources/hermes-agent`, audited commit `bfc84bdc6f85c14715e06d5fa83192ea3e7c7f79`.
- Reconciled inputs:
  - `reports/PHASE_8A_BIS_HERMES_SOURCE_CAPABILITY_MATRIX.md`
  - `reports/PHASE_8A_BIS_HERMES_EXTRACTION_PLAN.md`
  - `reports/PHASE_8A_BIS_HERMES_VS_STRIX_GAP_ANALYSIS.md`
  - `reports/PHASE_8A_BIS_HERMES_SOURCE_TREE.txt`
  - `reports/PHASE_8A_BIS_HERMES_CAPABILITY_GREP.txt`
  - `extensions/hermes_patterns/README.md`
  - `docs/HERMES_PATTERN_INTEGRATION_ARCHITECTURE.md`
  - `docs/PROJECT_SYNOPSIS.md`

## Non-negotiable boundaries
- No Hermes code copied, executed, imported, vendored, installed, or integrated.
- No Hermes runtime, gateway, provider/plugin host, toolset, scheduler, terminal backend, or self-improvement loop was created.
- `external_sources/hermes-agent` remains ignored and uncommitted.
- STRIX remains the sole core; Saga Fusion remains its own governance/reporting/control layer.
- R4 still requires approval; R5 remains blocked; `SandboxController` remains the execution boundary.
- No Agent Zero, OpenCLAW, Qwen, TurboQuant, llama.cpp, WSL2, real Telegram, real CloudOps, external pentest, tokens, or real `.env` were touched.
- This phase produced only docs/reports/status updates and validation.

## Priority reconciliation
| priority | reconciled decision | clean-room target |
|---|---|---|
| A Extension governance | Hermes-like breadth is useful only as metadata/provenance governance. Runtime plugin loading is out of scope. | 8C schema/manifest docs, disabled by default. |
| B Skill/plugin metadata schema | STRIX needs owner/source/license/risk/default-disabled fields; Hermes skill content is not imported. | 8C STRIX-owned metadata schema and authoring checklist. |
| C Toolset scoping | Tool scopes must map to existing STRIX risk model and never bypass ToolRouter/ApprovalVerifier/SandboxController. | 8D scope taxonomy and loop circuit breakers. |
| D Dry-run scheduler/cron patterns | Scheduler starts as non-executing audit specifications with timezone, budget, owner, evidence. | 8E dry-run only. |
| E Session recovery | Recovery must prove route/user/session ownership and record restart drain safely. | 8F STRIX state machine design. |
| F Context compression safety | Compaction summaries are non-authoritative and cannot compress away policy/redaction/approval invariants. | 8F summary template and regression matrix. |
| G Evidence manifests | Reports/evidence need standardized manifests with provenance, redaction status, and test provenance. | 8G manifest schema. |
| H LLM error taxonomy | Recovery is reporting-first; no automatic provider fallback or credential rotation. | 8H taxonomy and bounded retry records. |
| I Approval timeout tests | Timeout means deny; no allow-always; stale/channel/user/hash mismatch deny. | 8I approval regression matrix. |
| J Tool loop guardrails | Repeated failures/no-progress must halt and evidence, not repeat indefinitely. | 8D circuit breakers. |

## Phase design backlog

### Phase 8C — Skill/Plugin Metadata Governance
- **Objective:** Define STRIX-owned metadata and governance contracts for defensive skills, workflows, and future extensions without runtime plugin loading.
- **Observed Hermes pattern:** Hermes uses SKILL.md catalogs, optional skill roots, plugin.yaml manifests, indexes, reload commands, and provider/platform plugin directories.
- **Current STRIX/Saga Fusion equivalent:** STRIX has deterministic defensive workflows in saga_fusion/workflows, PatternRegistry entries, docs-only extensions/hermes_patterns, and no runtime plugin host.
- **Gap:** No formal extension manifest schema, provenance fields, risk tier, disabled-by-default lifecycle, allowlisted roots, or safe authoring checklist.
- **Clean-room strategy:** Create a STRIX schema/documentation package and static validators for metadata only. Treat all extension text as untrusted data; no dynamic import, no execution, no Hermes content ingestion.
- **Expected files:**
  - extensions/hermes_patterns/README.md
  - docs/HERMES_PATTERN_INTEGRATION_ARCHITECTURE.md
  - reports/PHASE_8C_SKILL_PLUGIN_METADATA_GOVERNANCE_REPORT.md
  - tests/* only if a later implementation phase explicitly adds validators
- **Required tests:**
  - metadata schema validation rejects missing provenance/risk tier
  - untrusted skill text cannot enter system/developer prompts
  - extension remains disabled by default
  - full pytest
- **Risks:**
  - untrusted instructions imported as active prompts
  - side-effecting plugin imports
  - dependency or token creep
- **Acceptance criteria:**
  - schema documents owner/source/license/risk/default_disabled/allowed_capabilities
  - Hermes code/content absent
  - STRIX policy authority unchanged
  - tests green
- **What NOT to do:**
  - do not load Hermes skills
  - do not implement a plugin host
  - do not import provider plugins
  - do not execute extension code

### Phase 8D — Toolset Scoping + Tool Loop Guardrails
- **Objective:** Strengthen Saga Fusion tool scope design and loop/failure boundaries while preserving ToolRouter, ApprovalVerifier, and SandboxController authority.
- **Observed Hermes pattern:** Hermes has tool kind mappings, idempotent/mutating taxonomy, toolset scoping, API toolset checks, no-progress and repeated-failure guardrails.
- **Current STRIX/Saga Fusion equivalent:** STRIX has saga_fusion/tool_routing, tool_guard, MissionPolicy, DangerousActionPolicy, and declarative execution plans.
- **Gap:** Limited explicit loop/no-progress counters, per-tool scope budgets, and mutating/idempotent evidence vocabulary for future adapters.
- **Clean-room strategy:** Design STRIX-native tool scope metadata and circuit-breaker criteria. Mutating tools always require policy/approval/sandbox checks; repeated failures become blocked evidence, not retries forever.
- **Expected files:**
  - docs/HERMES_PATTERN_INTEGRATION_ARCHITECTURE.md
  - reports/PHASE_8D_TOOLSET_SCOPING_GUARDRAILS_REPORT.md
  - tests/tool_routing/* if implementation approved
- **Required tests:**
  - same tool/no-progress loop halts
  - mutating tool cannot bypass R4/R5
  - unknown toolset is blocked
  - SandboxController remains mandatory
  - full pytest
- **Risks:**
  - looping noisy evidence
  - repeated real operations in later adapters
  - toolset bypass of policy
- **Acceptance criteria:**
  - bounded retry/loop policy documented
  - tool scopes map to STRIX risk model
  - no external tool execution in tests
  - tests green
- **What NOT to do:**
  - do not add Hermes gateway toolsets
  - do not add a parallel tool runtime
  - do not execute external pentest/CloudOps/Telegram real

### Phase 8E — Dry-Run Scheduler/Cron Patterns
- **Objective:** Design non-executing scheduled audit specifications with explicit timezone, owner, scope, budgets, and evidence manifests.
- **Observed Hermes pattern:** Hermes includes cron scheduler/jobs/CLI tests for next-run calculation, workdir handling, context sources, inactivity timeout, file permissions, and delivery paths.
- **Current STRIX/Saga Fusion equivalent:** STRIX has no active Saga cron module; workflows/task plans/reporting are interactive and evidence-only.
- **Gap:** No schedule policy, dry-run job spec, per-job evidence manifest, timezone capture, stale-approval handling, or delivery traceability.
- **Clean-room strategy:** Start with docs and dry-run schedule plan objects only. Scheduled jobs may produce plans/reports but may not execute actions; future execution requires R4 approval and SandboxController.
- **Expected files:**
  - reports/PHASE_8E_DRY_RUN_SCHEDULER_CRON_PATTERNS_REPORT.md
  - docs/HERMES_PATTERN_INTEGRATION_ARCHITECTURE.md
  - saga_fusion/scheduler/* only in later approved implementation
  - tests/scheduler/* only in later approved implementation
- **Required tests:**
  - schedule spec records timezone
  - job is execution_allowed=false
  - R4/R5 scheduled intents do not execute
  - stale/pending approval blocks
  - full pytest
- **Risks:**
  - unattended stale instructions
  - cron loops
  - misrouted reports
  - timezone drift
- **Acceptance criteria:**
  - dry-run only
  - owner/scope/budget/evidence required
  - no real CloudOps/Telegram/external calls
  - tests green
- **What NOT to do:**
  - do not wire OS cron
  - do not execute scheduled commands
  - do not send real Telegram
  - do not create unattended CloudOps

### Phase 8F — Session Recovery + Context Compression Safety
- **Objective:** Design STRIX-owned recovery and compaction rules that preserve user/session routing, approvals, policy constraints, and redaction boundaries.
- **Observed Hermes pattern:** Hermes has gateway session persistence, restart/pending drain, task-local context, session expiry, context compression, protected head/tail, structured summaries, tool-output pruning, and compaction tests.
- **Current STRIX/Saga Fusion equivalent:** STRIX has Telegram gating, mission memory, context windows, session summarizer, prompt builder, and non-authoritative memory policy.
- **Gap:** No persistent restart-drain state machine, no route recovery design, no token-aware compressor, and no compaction-boundary regression matrix.
- **Clean-room strategy:** Design a STRIX recovery state machine and compaction template where summaries are explicitly non-authoritative. Never compress away R4/R5 policy, SandboxController boundary, redaction requirements, approval IDs/action hashes, or current user routing.
- **Expected files:**
  - reports/PHASE_8F_SESSION_RECOVERY_CONTEXT_COMPRESSION_SAFETY_REPORT.md
  - docs/HERMES_PATTERN_INTEGRATION_ARCHITECTURE.md
  - tests/memory/* or tests/session_recovery/* if implementation approved
- **Required tests:**
  - summary cannot override policy
  - secret text is redacted before/after compaction
  - approval hash survives recovery
  - wrong-user session restore rejected
  - restart drain records pending state
  - full pytest
- **Risks:**
  - cross-user report/approval routing
  - prompt injection promoted by summary
  - loss of denial reasons
  - secret leakage
- **Acceptance criteria:**
  - recovery states documented
  - compaction summary labeled non-authoritative
  - route/session identifiers redacted in evidence
  - tests green
- **What NOT to do:**
  - do not import Hermes gateway
  - do not create multi-platform gateway
  - do not store raw secrets
  - do not let summaries change policy

### Phase 8G — Evidence/Reporting Manifests
- **Objective:** Standardize evidence/report artifact manifests with provenance, phase, redaction, validation, and delivery metadata.
- **Observed Hermes pattern:** Hermes uses trajectories/evidence stores, dashboard/package manifests, delivery notices, and reporting tests.
- **Current STRIX/Saga Fusion equivalent:** STRIX has saga_fusion/reporting, evidence logs, phase reports, TEST_RESULTS_SUMMARY, SECURITY_REGRESSION_REPORT, and risk register updates.
- **Gap:** Artifact manifests are not yet a single standardized schema across phase reports, evidence JSON, redaction status, and test provenance.
- **Clean-room strategy:** Define a STRIX manifest schema for generated evidence and reports. Include source phase/commit, generator, redaction status, validation commands/results, and non-secret delivery references.
- **Expected files:**
  - reports/PHASE_8G_EVIDENCE_REPORTING_MANIFESTS_REPORT.md
  - docs/HERMES_PATTERN_INTEGRATION_ARCHITECTURE.md
  - reports/evidence/* only if generated by STRIX-owned code
- **Required tests:**
  - manifest schema validates required fields
  - sensitive metadata redacted
  - report references manifest
  - missing test provenance fails validation
  - full pytest
- **Risks:**
  - manifest leaks local paths/tokens
  - false provenance
  - report/evidence drift
- **Acceptance criteria:**
  - manifest schema documented
  - redaction status explicit
  - validation commands/results recorded
  - tests green
- **What NOT to do:**
  - do not include real tokens/.env
  - do not include external_sources contents
  - do not add dashboard runtime

### Phase 8H — LLM Error Taxonomy + Recovery
- **Objective:** Design centralized LLM/provider error classification and recovery reporting without automatic credential rotation or unapproved fallback.
- **Observed Hermes pattern:** Hermes classifies API errors and suggests retry, credential rotation, fallback, compression, abort, and provider-specific recovery paths.
- **Current STRIX/Saga Fusion equivalent:** STRIX LLM gateway is disabled by default, env-driven, redacted, mocked in tests, with safe router fallback and no tool execution from brain output.
- **Gap:** No central error taxonomy, retry budget evidence, or safe fallback decision record for LLM failures.
- **Clean-room strategy:** Classify errors into transient, auth, rate-limit, context-length, safety, provider, and unknown categories. Recovery is reporting-first; no credential rotation, no hidden provider fallback, no policy downgrade.
- **Expected files:**
  - reports/PHASE_8H_LLM_ERROR_TAXONOMY_RECOVERY_REPORT.md
  - docs/HERMES_PATTERN_INTEGRATION_ARCHITECTURE.md
  - saga_fusion/llm/* only if implementation approved
  - tests/llm/* only if implementation approved
- **Required tests:**
  - auth failures do not retry indefinitely
  - rate limit uses bounded budget
  - context error suggests compression without policy loss
  - fallback records reason
  - full pytest
- **Risks:**
  - masking auth/billing problems
  - provider fallback data leakage
  - unsafe retry storms
- **Acceptance criteria:**
  - taxonomy documented
  - no automatic credential rotation
  - recovery decisions evidenced/redacted
  - tests green
- **What NOT to do:**
  - do not touch Qwen/TurboQuant/llama.cpp/WSL2
  - do not call real LLM in tests
  - do not rotate or read secrets
  - do not add unapproved providers

### Phase 8I — Approval Timeout + Regression Depth
- **Objective:** Expand design and tests for timeout-to-deny, stale approvals, channel-specific audit outcomes, and risk-based regression categories.
- **Observed Hermes pattern:** Hermes approval tests cover allow/deny callbacks, timeout-to-deny behavior, CLI/gateway approval UI, restart cases, cron/session/tool regression breadth.
- **Current STRIX/Saga Fusion equivalent:** STRIX has ApprovalVerifier, Telegram approval workflow, approval IDs, action hashes, replay protection, R4 approval-required, and R5 blocked.
- **Gap:** Need explicit multi-channel timeout-to-deny regression design, stale scheduled approval handling, and matrix coverage across scheduler/session/tool/error/manifest features.
- **Clean-room strategy:** Codify R4 timeout as deny, never allow-always. Require exact action hash and current session/user/channel; expand regression matrix with docs-first acceptance before future code.
- **Expected files:**
  - reports/PHASE_8I_APPROVAL_TIMEOUT_REGRESSION_DEPTH_REPORT.md
  - docs/HERMES_PATTERN_INTEGRATION_ARCHITECTURE.md
  - tests/approval/* if implementation approved
- **Required tests:**
  - expired approval denies
  - timeout produces audit event
  - hash mismatch denies
  - wrong channel/user denies
  - R5 remains non-approvable
  - full pytest
- **Risks:**
  - stale approval reuse
  - allow-always weakening
  - approval/report route mismatch
  - regression blind spots
- **Acceptance criteria:**
  - timeout-to-deny documented
  - approval evidence includes channel/session/hash
  - R5 non-approvable invariant preserved
  - tests green
- **What NOT to do:**
  - do not implement allow-always
  - do not approve broad toolsets
  - do not bypass SandboxController
  - do not execute real actions

## Cross-phase invariants
- Every implementation phase must cite the Hermes source-path pattern conceptually, then implement only STRIX-owned behavior.
- Every future code phase needs focused tests plus `python3 -m pytest tests -q --tb=short`.
- Documentation must distinguish `ADAPT_PATTERN`, `REIMPLEMENT_CLEAN`, `DOCUMENT_ONLY`, `DISCARD`, and `FUTURE_RESEARCH`.
- Any future execution adapter must pass through STRIX policy, approval, sandbox, evidence, reporting, and redaction controls.

## Validation plan for this design phase
- Validate JSON backlog syntax.
- Run full STRIX suite: `python3 -m pytest tests -q --tb=short`.
- Commit only explicit docs/reports/status files after tests pass.
