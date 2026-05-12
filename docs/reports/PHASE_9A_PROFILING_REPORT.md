# STRIX Phase 9A Profiling Report

**Project:** STRIX ELITE CYBER AGENT  
**Phase:** 9A — Performance Profiling / No Behavior Change  
**Report date:** 2026-05-12  
**Baseline commit inspected:** `e581793 phase 9: add optimization planning document`  
**Scope:** profiling/inspection only; no optimization, refactor, runtime, security, R4/R5, config, `.env`, token, Hermes, Telegram-real, LLM-real, CloudOps, or pentest behavior changes.

## Source Availability Caveat

Required source reads were performed against available local project files. `docs/SECURITY_MODEL.md` and `docs/STRIX_RISK_REGISTER.md` were not present in this checkout. The root `STRIX_RISK_REGISTER.md` was used instead, together with `docs/planning/PHASE_9_OPTIMIZATION_PLAN.md` and `docs/reports/PHASE_8_CLOSURE_REPORT.md`.

## Methodology

Phase 9A used read-only/static and deterministic local-only inspection:

1. Reviewed Phase 9 plan, Phase 8 closure report, root risk register, relevant Saga Fusion modules, and relevant tests for approval, LLM, manifests, Telegram, sandbox, reporting, and security.
2. Performed static complexity inspection using an AST script run from the shell only; no script was committed.
3. Ran deterministic local micro-profiling/timeit/cProfile using in-memory mock inputs and temporary files under `/tmp` only.
4. Used disabled-LLM fallback paths and Telegram mock configuration only.
5. Did not read/print `.env`, tokens, external API secrets, or runtime configs.
6. Did not execute real Telegram, real LLM, CloudOps, pentest, Hermes, or production/external actions.
7. Did not change production code or behavior.

## Validation Commands

- `python3 -m pytest tests/approval tests/llm tests/manifests tests/telegram tests/sandbox tests/reporting tests/security -q --tb=short --durations=20`
  - Result: **153 passed / 0 failed / 1 existing warning** in 0.22s.
- `python3 -m pytest tests -q --tb=short --durations=20`
  - Result: **334 passed / 0 failed / 3 existing warnings** in 2.37s.
  - Slowest visible test: `tests/unit/test_process_guard.py::test_run_command_timeout` at 2.01s.

The warnings are the already-known coroutine-not-awaited warnings recorded in Phase 8/9 planning history.

## Static Complexity Hotspots

| Module/path | Hot function/path | Static complexity signal | Notes |
|---|---:|---:|---|
| `saga_fusion/telegram/mission_operator.py` | `TelegramMissionOperator.handle_message` | C39 | Primary orchestration hotspot: authorization, commands, prompt security, LLM fallback, task planning, memory, tool routing, policy, approval, evidence, sandbox dispatch. High complexity creates regression risk for Phase 9C even if runtime is fast today. |
| `saga_fusion/manifests/validator.py` | `_validate_artifact` | C20 | Multiple mandatory safety checks: ref/path, non-execution, non-authoritative, SHA-256 format, optional path hash verification, sensitive redaction, forbidden metadata, secret-like metadata detection. |
| `saga_fusion/manifests/validator.py` | `validate` | C13 | Rebuilds artifact lists and validates report/evidence link integrity. |
| `saga_fusion/session/compressor.py` | `compress` | C10 | Iterates context, extracts text, redacts, neutralizes instructions, joins, truncates, and tracks exclusion metadata. |
| `saga_fusion/runtime/sandbox/sandbox_controller.py` | `_effective_mode`, `execute`, `validate_action` | C10/C6/C6 | Boundary logic is small but security-critical; no behavior optimization should start here without golden tests. |
| `saga_fusion/approval/approval_verifier.py` | `verify` | C10 | TTL, R5, replay, terminal state, hash, and actor checks are performance-light but safety-critical. |
| `saga_fusion/telegram/mission_policy.py` | `classify_risk` | C9 | Re-evaluates dangerous-action policy and canonical action per request; candidate for Phase 9C only with no-decision-change matrix. |
| `saga_fusion/llm/brain_service.py` | `build_mission_from_natural_language` | C8 | Disabled/fallback path is cheap; enabled path includes recovery, parsing, unsafe-output classification. |
| `saga_fusion/memory/context_window.py` | `_rank`, `select` | C7/C7 | Sorts eligible context items and ranks by evidence/approval/constraint strings. |
| `saga_fusion/reporting/report_builder.py` | `build_mission_report` | C7 | Repeated recursive redaction over mission/findings/approvals/evidence is the dominant reporting cost. |

## Micro-Profiling Results

All measurements below used local mock/in-memory safe inputs. Values are directional, not production benchmarks.

| Path measured | Input | Result |
|---|---|---:|
| `MissionPolicy.classify_risk` | 4 mock mission requests, repeated 2,000 times | 0.220852s total; ~110.43µs per 4 classifications |
| `PromptSecurityLayer.guard_for_llm` | 3 benign/injection/bypass texts, repeated 1,000 times | 0.028628s total; ~28.63µs per 3 guards |
| `SandboxController.execute` dry-run | safe `/tmp` dry-run action, repeated 2,000 times | 0.020993s total; ~10.50µs per call |
| `ApprovalVerifier.verify` replay path | one already-approved/replay approval, repeated 1,000 times | 0.001414s total; ~1.41µs per call |
| `ApprovalVerifier.verify` fresh approvals | 1,000 pending approvals verified once | 0.001362s total; ~1.36µs per approval |
| `LLMRouter` disabled fallback | natural-language mission fallback, repeated 2,000 times | 0.024966s total; ~12.48µs per call |
| `ManifestBuilder` path refs | evidence+report refs for small `/tmp` files, repeated 500 times | 0.017536s total; ~35.07µs per pair |
| `ManifestValidator` reporting manifest | one report + one evidence ref, repeated 2,000 times | 0.067947s total; ~33.97µs per validation |
| `ReportBuilder.build_mission_report` | 100 evidence records, repeated 500 times | 0.599048s total; ~1.20ms per report |
| `TelegramReportFormatter.format` | one report, repeated 1,000 times | 0.046511s total; ~46.51µs per format |
| `ContextWindow.select+render` | 200 context items, repeated 500 times | 0.092910s total; ~185.82µs per render |
| `ContextCompressor.compress` | 200 context items, repeated 500 times | 1.222763s total; ~2.45ms per compression |
| Telegram mock status+approval flow | status + R4 approval + approval command, repeated 200 times | 0.262404s total; ~1.31ms per flow |
| `SagaContextManager.collapse_history` | 500 x 1,000-char messages | ~0.07–0.14ms per collapse; collapsed to summary path |

Telegram mock cProfile top internal hotspot for one status+approval flow was evidence redaction/logging: `TelegramMissionOperator.handle_message`, `EvidenceLogger._record`, `_redact_mapping`, and `TelegramSecurity.redact_secrets`. Total flow was still ~3ms under cProfile instrumentation.

## Critical Paths Detected

1. **Telegram mock mission flow**  
   `TelegramMissionOperator.handle_message` chains: evidence logging → rate limit → authorization → command parse → prompt security or mission parse → task planning → memory render → MissionPolicy → ToolRouter → approval or sandbox dry-run → reporting/evidence state. The individual components are fast, but the orchestration function is complex and repeats redaction/evidence serialization.

2. **Policy classification path**  
   `MissionPolicy.classify_risk` calls `DangerousActionPolicy.evaluate` over a joined action/target/arguments/raw_text string, then calls `canonicalize_action` when dangerous policy does not already return blocked/approval-required. Hotspot is not current latency; risk is future caching/normalization accidentally changing highest-risk-wins behavior.

3. **Prompt security validation/redaction path**  
   `PromptSecurityLayer.guard_for_llm` runs detector once, policy once, sanitizer once. It is fast today. The main repeated-validation risk is that callers using `evaluate()` and `sanitize()` separately would run detection twice; `guard_for_llm()` is the preferred one-pass path.

4. **Approval verification path**  
   `ApprovalVerifier.verify` is extremely fast. Safety checks are sequential and deterministic: not found, R5, replay, terminal state, expiry, action hash, actor allowlist, then non-executing approval. Do not optimize this until a golden matrix proves exact status/reason/evidence preservation.

5. **Sandbox boundary path**  
   `SandboxController.validate_action` and dry-run `execute` are fast. `_effective_mode` has normalization logic for string/enum modes. This path is security-critical and should not be modified in 9B/9C unless explicitly in scope with regression tests.

6. **LLM router/brain fallback path**  
   Disabled LLM fallback is cheap and non-executing. Enabled path has more recovery and unsafe-output validation logic but was not externally exercised. Ambient `STRIX_LLM_ENABLED` remains a test-isolation risk from Phase 8H/8I history.

7. **Manifest/reporting pipeline**  
   Manifest refs and validation are fast for small artifacts. Reporting dominates local micro-profiles through recursive redaction over evidence lists. `ManifestValidator` can re-hash existing local paths; that is correct but becomes I/O-bound for large artifacts.

8. **Context compression/collapse path**  
   Legacy `SagaContextManager.collapse_history` is fast and simple. Newer `ContextCompressor.compress` is more expensive because it redacts and neutralizes every item; it is the clearest memory/context optimization candidate for 9B.

## Hotspots by Complexity

- **Highest:** `TelegramMissionOperator.handle_message` (C39). Recommendation: do not refactor in 9A; in 9C consider extracting test-preserving pure helper functions only after golden Telegram/approval behavior matrix exists.
- **High:** `ManifestValidator._validate_artifact` (C20). Recommendation: preserve as safety-critical; only consider reducing repeated list construction or hash rechecks in 9D with exact validation equivalence tests.
- **Medium-high:** `ContextCompressor.compress`, `ApprovalVerifier.verify`, `SandboxController._effective_mode`, `MissionPolicy.classify_risk`. Recommendation: approval/sandbox are not performance priorities despite complexity; context and policy are better candidates.

## Hotspots by Memory / Allocation

- `ContextCompressor.compress` builds per-item extracted text, redacted text, inert strings, rendered list, and final joined string. Cost grows with item count and content length. This is the leading Phase 9B candidate.
- `ContextWindow.select` filters a candidate list, sorts it, then renders selected items. Sorting is acceptable at current scale but can dominate if memory grows.
- `ReportBuilder.build_mission_report` recursively redacts mission/findings/approvals/evidence into separate structures, then stores full redacted evidence in a report section. This is the leading Phase 9D candidate.
- `EvidenceReporter.load` and `ReportBuilder.build_from_evidence` read evidence files fully into memory. This was not changed; future 9D should consider streaming only if report semantics stay identical and secrets remain redacted.
- `ManifestValidator.validate` materializes combined artifact lists. Small now; for large manifests, this is a moderate candidate after safety tests.

## Hotspots by Repeated Validation / Redaction

- `PromptSecurityLayer.evaluate()` plus `sanitize()` separately would repeat detector work. `guard_for_llm()` already avoids that. Recommendation for 9C: prefer existing guard path; do not change detection semantics.
- Telegram evidence logging repeatedly calls `TelegramSecurity.redact_secrets` through `_record` and response serialization. This is safe but repeated. Recommendation for 9C/9D: only consider single-pass redaction metadata if tests prove no secret regression.
- `ReportBuilder.build_mission_report` redacts each input category independently and then formatter/report consumers may redact/serialize again. Candidate for 9D.
- `ManifestBuilder` redacts provenance/metadata on ref creation, and `ManifestValidator` scans metadata again. This is intentional defense-in-depth; do not remove in 9D unless equivalent safety metadata is proven.
- `MissionPolicy.classify_risk` and `ToolRouter.route_tool_request` both evaluate action risk in the Telegram path. This is a candidate for 9C only if highest-risk-wins and R4/R5 preservation are proven by tests.

## Optimization Risks by Module

| Module | Risk if optimized incorrectly | Required guardrail |
|---|---|---|
| `saga_fusion/telegram/mission_policy.py` | R4/R5 downgrade, canonicalization drift, dangerous-action bypass. | Golden decision matrix for ES/EN destructive, deploy, scan, status, secret/exfiltration, and bypass prompts. |
| `saga_fusion/prompt_security/` | Prompt injection missed or sanitized text leaks suspicious segments incorrectly. | Keep detector+policy+sanitizer outputs identical for existing corpus. |
| `saga_fusion/runtime/sandbox/` | Execution boundary weakened or dry-run/local mode semantics changed. | No 9B/9C changes unless explicitly approved; sandbox/security full tests mandatory. |
| `saga_fusion/approval/` | TTL, hash, replay, actor, denial, terminal-state, or R5 behavior regression. | Approval regression matrix must remain exact, including `execution_allowed=False`. |
| `saga_fusion/llm/` | Real LLM calls in tests, infinite retry, hidden auth/billing failures, unsafe fallback. | Disable ambient LLM in tests; recovery metadata and fallback non-execution must remain. |
| `saga_fusion/manifests/` | Artifact body read, raw metadata embedded, tamper detection weakened. | Keep reference-only semantics; hash/provenance/redaction validation unchanged. |
| `saga_fusion/reporting/` | Secret leakage through reports or Telegram summaries. | ReportRedactor and output budget behavior must remain mandatory. |
| `saga_fusion/session/` and `saga_fusion/memory/` | Compressed/retrieved context becomes authoritative, leaks secrets, or downgrades policy. | Preserve `non_authoritative=True`, `execution_allowed=False`, secret exclusion, and R4/R5 no-downgrade. |
| `saga_fusion/telegram/mission_operator.py` | Mock/real gating, approval flow, evidence, or LLM isolation drift. | Keep real Telegram untouched; use deterministic `/mission` paths in tests. |

## Recommendations for Phase 9B / 9C / 9D

### Phase 9B — Context and Memory Optimization

1. Focus on `ContextCompressor.compress` and `ContextWindow.select/render` first.
2. Preserve secret exclusion and neutralized/non-authoritative output exactly.
3. Add golden tests around compressed text, excluded secret count, truncation marker, `non_authoritative=True`, and `execution_allowed=False` before changing internals.
4. Avoid modifying legacy `SagaContextManager.collapse_history` unless a specific failing performance case appears; it is currently fast.

### Phase 9C — Policy Evaluation Optimization

1. Start with measurement-backed decision-cache design only for deterministic pure inputs.
2. Candidate: reduce duplicate action string assembly/canonicalization between MissionPolicy and downstream routing, but only with exact decision equivalence tests.
3. Leave `ApprovalVerifier` and `SandboxController` behavior untouched unless a dedicated safety subphase approves changes.
4. Keep `PromptSecurityLayer.guard_for_llm()` as the one-pass API; avoid separate evaluate/sanitize calls in new paths.

### Phase 9D — Reporting / Manifest Pipeline Optimization

1. Focus on `ReportBuilder.build_mission_report` recursive redaction overhead for large evidence lists.
2. Consider streaming or summarized evidence only if existing report sections and Telegram summaries remain semantically equivalent for current tests, and no raw evidence bodies/secrets are introduced.
3. Preserve `ManifestBuilder` reference-only artifact handling: no artifact body reads for secret scanning.
4. Preserve `ManifestValidator` tamper checks and sensitive redaction enforcement. If avoiding repeated hash checks, require explicit immutable metadata or caller-provided validation state with tests.

## Prohibited Optimizations

- Do not change R4/R5 classification decisions.
- Do not cache decisions across different users, chats, mission IDs, action hashes, approval states, or timestamps.
- Do not remove PromptSecurity, MissionPolicy, ApprovalVerifier, ToolRouter/ScopedToolRouter, ManifestValidator, ReportRedactor, EvidenceLogger, or SandboxController checks.
- Do not remove defense-in-depth redaction unless replacement tests prove identical or stricter redaction.
- Do not read artifact bodies for manifest secret scanning.
- Do not convert approval success into execution.
- Do not introduce real Telegram, real LLM, CloudOps, pentest, OS cron, Hermes runtime/code, or production/external execution.
- Do not touch `.env`, tokens, runtime configs, `SandboxController` behavior, Approval execution boundary, MissionPolicy R4/R5 behavior, or Hermes code.
- Do not stage `external_sources/` or old untracked Phase 6B-4 reports/logs.

## Mandatory Test Matrix That Must Stay Green

| Area | Required tests before 9B/9C/9D commits |
|---|---|
| Approval/HITL | `tests/approval`, Telegram approval regression paths |
| LLM/fallback/recovery | `tests/llm` with ambient real LLM disabled/mocked |
| Manifest/reporting | `tests/manifests`, `tests/reporting` |
| Telegram mock/gating | `tests/telegram` |
| Sandbox/security boundary | `tests/sandbox`, `tests/security` |
| Prompt security | `tests/prompt_security` |
| Memory/session/context | `tests/memory`, `tests/session`, `tests/unit/test_context_manager.py` |
| Tool routing/scoping/skills | `tests/tool_routing`, `tests/tool_scoping`, `tests/skills` |
| Scheduler dry-run | `tests/scheduler` |
| Full regression | `python3 -m pytest tests -q --tb=short` |

Minimum Phase 9B/9C/9D sequence: targeted module tests → cross-cutting safety subset → full suite → changed-file secret scan → `git status --short` hygiene check.

## GO / NO-GO for Phase 9B

**Verdict: GO for Phase 9B planning and narrowly-scoped context/memory optimization design; conditional GO for implementation only after adding/confirming golden behavior tests.**

Rationale:

- Phase 9A found no need for broad refactor or behavior changes.
- Full suite remains green at the Phase 8/9 baseline: 334 passed / 3 existing warnings.
- The strongest evidence-backed 9B target is context/memory compression/rendering overhead, especially `ContextCompressor.compress`.
- Approval and sandbox paths are fast and security-critical; they should not be optimized in 9B.
- Reporting/manifest work should wait for 9D.
- Policy classification changes should wait for 9C and a no-decision-change matrix.

