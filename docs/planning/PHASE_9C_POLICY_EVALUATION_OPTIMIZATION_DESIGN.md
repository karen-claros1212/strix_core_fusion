# Phase 9C Policy Evaluation Optimization Design

**Project:** STRIX ELITE CYBER AGENT  
**Phase:** 9C — Policy Evaluation Optimization Design  
**Document type:** Planning only / no optimization implementation  
**Created:** 2026-05-12  
**Baseline:** `e345cd9 phase 9b: add closeout report`  
**Canonical validation baseline:** `python3 -m pytest tests -q` → 346 passed / 0 failed / 3 existing warnings

## Goal

Design a safe, narrow optimization path for policy evaluation hot paths without changing security behavior.

Phase 9C must start with profiling and golden behavior tests. No runtime code, policy semantics, risk tiers, approval behavior, sandbox boundaries, redaction behavior, or external integrations may change during this planning step.

## Candidate Areas to Profile

1. **MissionPolicy risk classification**
   - Spanish/English action normalization.
   - DangerousActionPolicy pre-check.
   - Highest-risk-wins behavior.
   - R4/R5 classification paths.

2. **PromptSecurity normalization / unsafe pattern checks**
   - PromptInjectionDetector matching.
   - PromptSanitizer normalization/marking.
   - PromptPolicy ALLOW/WARN/BLOCK/ESCALATE decisions.

3. **SandboxPolicy / SandboxController boundary checks**
   - Effective sandbox mode selection.
   - Dry-run dispatch metadata.
   - Denied/non-executing action handling.

4. **Approval gate decision paths**
   - Approval expiry.
   - Replay/used state.
   - Action hash matching.
   - Authorized actor checks.
   - R5 non-approvable handling.

5. **Redaction-sensitive policy metadata handling**
   - Evidence/reporting redaction.
   - LLM error evidence redaction.
   - Manifest/report metadata redaction.
   - Non-authoritative context/report/evidence metadata preservation.

## Non-Goals

- No behavior changes.
- No new permissions.
- No R4/R5 downgrade.
- No approval bypass.
- No direct execution enablement.
- No Telegram runtime activation.
- No LLM runtime activation.
- No CloudOps runtime activation.
- No pentest runtime activation.
- No external source execution.
- No Hermes integration.
- No broad refactor.
- No test changes in this planning-only phase.

## Required Invariants

- R5 remains blocked.
- R4 remains `approval_required`.
- Approved action does not execute automatically unless existing sandbox rules allow it in a later explicitly approved phase.
- Spanish/English command normalization must preserve risk classification.
- Redaction must remain intact.
- Prompt injection must remain neutralized or blocked according to existing PromptSecurity rules.
- `execution_allowed` must not be widened.
- Non-authoritative evidence/report/context metadata remains non-authoritative.
- No secrets are persisted or logged.
- Policy decisions remain deterministic for identical inputs.
- SandboxController remains the execution boundary.
- ToolRouter/ScopedToolRouter remain non-executing route/planning layers.
- Approval success remains non-executing in current Telegram approval flow.

## Proposed Golden Tests Before Implementation

Golden tests must be added and passing before any Phase 9C optimization implementation.

| Golden test | Required outcome |
|---|---|
| Spanish dangerous create command | Remains R4 / `approval_required` where applicable. |
| Spanish dangerous delete/wipe command | Remains R5 / blocked. |
| English dangerous create command | Remains R4 / `approval_required` where applicable. |
| English dangerous delete/wipe command | Remains R5 / blocked. |
| Benign read-only command | Remains low risk / non-executing. |
| Prompt injection attached to benign request | Does not downgrade risk or bypass PromptSecurity. |
| Prompt injection attached to R4/R5 request | R4/R5 classification preserved or escalated, never downgraded. |
| Approval-required action without valid approval | Cannot execute. |
| Expired approval | Remains blocked. |
| Unauthorized actor approval | Remains blocked. |
| Hash mismatch approval | Remains blocked. |
| Redacted secret through policy evaluation | Secret remains redacted in evidence/metadata. |
| Same input repeated | Identical policy output / deterministic decision. |
| `.env` access guard | Policy evaluation does not read `.env`. |
| Real LLM guard | Policy evaluation does not call real LLM. |
| Real Telegram guard | Policy evaluation does not call real Telegram. |
| CloudOps/pentest guard | No real CloudOps or pentest execution. |
| Hermes guard | No Hermes execution/import dependency. |

Recommended future test locations:

- `tests/policy/test_phase_9c_policy_golden.py`
- `tests/prompt_security/test_phase_9c_prompt_policy_golden.py`
- `tests/approval/test_phase_9c_approval_policy_golden.py`
- `tests/telegram/test_phase_9c_telegram_policy_golden.py`

## Profiling Plan

1. **Identify deterministic benchmark inputs**
   - Fixed Spanish/English R1/R4/R5 commands.
   - Fixed prompt-injection strings.
   - Fixed approval records for pending/expired/used/hash-mismatch/unauthorized states.
   - Fixed redaction-sensitive metadata containing synthetic non-real secret-like strings.

2. **Measure current policy evaluation latency**
   - Use `timeit` or `cProfile` on in-memory fixtures only.
   - Do not read `.env`, runtime configs, or external files.
   - Do not call real LLM, Telegram, CloudOps, pentest, or Hermes.

3. **Isolate hot loops only after golden tests exist**
   - Candidate loops: repeated normalization, repeated dangerous-action pattern scans, repeated prompt pattern checks, repeated redaction of identical metadata.
   - Do not cache across requests unless determinism, invalidation, and security isolation are proven.

4. **Compare output hashes before/after**
   - Serialize normalized policy decisions to stable dictionaries.
   - Hash golden outputs before optimization.
   - Require identical hashes after optimization.

5. **Accept only narrow optimizations with zero semantic delta**
   - Local helper extraction is acceptable only if golden output remains identical.
   - Precomputed local constants or bound methods may be acceptable.
   - Any optimization that changes R4/R5, redaction, prompt handling, approval, sandbox, or non-authoritative metadata is rejected.

## Optimization Risks by Area

| Area | Risk | Mitigation |
|---|---|---|
| MissionPolicy | Cached normalization may downgrade R4/R5. | Golden R4/R5 matrix with ES/EN inputs and highest-risk-wins assertions. |
| PromptSecurity | Pattern simplification may miss injection/bypass text. | Golden injection corpus and BLOCK/ESCALATE preservation. |
| SandboxController | Boundary checks may be bypassed by fast path. | No optimization until sandbox boundary golden tests exist. |
| ApprovalVerifier | Time/hash/user/replay checks may be reordered incorrectly. | Existing 8I tests plus 9C deterministic golden matrix. |
| Redaction metadata | Reduced redaction passes may leak secrets. | Changed-file secret scans and golden redaction tests. |
| Telegram policy path | Complex orchestration may hide semantic changes. | Use mock Telegram only with `/mission` deterministic inputs. |

## Validation Command

Canonical STRIX validation command:

```bash
python3 -m pytest tests -q
```

Do not use root-level `pytest -q` as canonical validation because it may collect ignored/external source checkouts such as `external_sources/hermes-agent`.

## Exit Criteria

Phase 9C planning is complete when:

- This planning document is committed and pushed.
- No runtime files are changed.
- Canonical STRIX test suite remains green.
- Local branch is even with `origin/main`.
- The next step is limited to Phase 9C golden behavior tests.

## GO / NO-GO Decision

- **GO:** Phase 9C golden behavior tests.
- **NO-GO:** Phase 9C optimization implementation until golden tests are added and pass.
- **NO-GO:** Any optimization that changes security semantics, risk tiers, approval requirements, redaction behavior, manifest behavior, or sandbox boundaries.
