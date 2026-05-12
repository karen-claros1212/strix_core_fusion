# STRIX Phase 9 Optimization Plan

**Project:** STRIX ELITE CYBER AGENT  
**Phase:** 9 — Original STRIX Optimization  
**Document type:** Planning only / no implementation  
**Created:** 2026-05-12  
**Baseline:** `ac9f36e phase 8: add closure report`  
**Last full validation:** 334 passed / 0 failed / 3 existing warnings

## Executive Summary

Phase 9 should optimize the original STRIX/Saga Fusion system without changing security semantics, approval boundaries, or runtime behavior by default. The phase must begin with measurement, regression preservation, and design validation before any performance or structural changes are allowed.

The main optimization target is not to make STRIX less controlled. The goal is to make STRIX faster, clearer, easier to maintain, and more predictable while preserving all Phase 8 safety boundaries.

## Phase 9 Objectives

1. Profile current STRIX/Saga Fusion performance without behavior changes.
2. Reduce unnecessary context/memory/report overhead while preserving redaction and non-authoritative context rules.
3. Optimize policy evaluation paths without weakening R4/R5, PromptSecurity, MissionPolicy, ApprovalVerifier, ToolRouter/ScopedToolRouter, Scheduler, Manifests, or SandboxController boundaries.
4. Improve reporting/manifest pipeline efficiency while keeping references/hash/provenance semantics intact.
5. Expand regression depth around the optimized paths before declaring Phase 9 complete.

## Security Boundaries Inherited from Phase 8

Phase 9 inherits these non-negotiable invariants:

- STRIX remains the single core.
- Saga Fusion remains the native governance/audit/extensibility layer.
- R4 actions require explicit human approval.
- R5 actions remain blocked and non-approvable.
- Approval success does not execute actions.
- SandboxController remains the execution boundary.
- ToolRouter and ScopedToolRouter remain non-executing route/planning layers.
- Scheduler remains dry-run metadata only by default.
- Session recovered/compressed context remains non-authoritative and cannot downgrade R4/R5.
- Manifests remain non-authoritative, reference-only, and `execution_allowed=False`.
- LLM recovery remains bounded, metadata-only for backoff, non-executing on fallback, and redacted.
- No real Telegram/CloudOps/pentest execution in Phase 9 planning or profiling.
- No real LLM calls in unit tests.
- No Hermes code copying, execution, or runtime integration.

## Candidate Modules for Optimization

| Area | Candidate modules | Optimization direction | Primary risk |
|---|---|---|---|
| Context and memory | `saga_fusion/memory/`, `saga_fusion/session/`, `saga_fusion/llm/prompt_builder.py` | Reduce redundant context serialization and repeated redaction passes. | Accidentally making memory authoritative or leaking secrets. |
| Policy evaluation | `saga_fusion/policy/`, `saga_fusion/prompt_security/`, `saga_fusion/telegram/mission_policy.py` | Cache deterministic classification decisions where safe; simplify repeated normalization. | Downgrading R4/R5 or bypassing prompt/security checks. |
| Tool routing/scoping | `saga_fusion/tool_routing/`, `saga_fusion/tool_scoping/`, `saga_fusion/skills/` | Avoid duplicate classification/scope calculations; preserve non-execution. | Tool outside scope accidentally allowed. |
| Approval path | `saga_fusion/approval/`, `saga_fusion/telegram/mission_operator.py` | Maintain fast deterministic verification and evidence summaries. | Replay/hash/unauthorized/expired edge cases regressing. |
| Reporting and manifests | `saga_fusion/reporting/`, `saga_fusion/manifests/`, `saga_fusion/evidence/` | Reduce duplicate redaction/rendering/hash validation while preserving reference-only manifest semantics. | Reading artifact content or embedding secrets. |
| LLM recovery | `saga_fusion/llm/` | Keep bounded recovery deterministic; avoid accidental ambient real LLM tests. | Infinite retries, sleeps, provider switching, or real calls in tests. |
| Scheduler | `saga_fusion/scheduler/` | Keep planning fast and deterministic. | Accidentally creating execution/run/cron behavior. |

## Regression Risks

1. **Security downgrade risk:** optimization might skip a policy layer or reuse stale decisions incorrectly.
2. **R4/R5 regression risk:** cached/collapsed classifications could downgrade approval-required or blocked actions.
3. **Secret leakage risk:** reducing redaction passes could expose tokens/API keys/Bearer strings in reports, manifests, memory, or errors.
4. **Execution boundary risk:** refactors might accidentally add direct execution surfaces to router/scheduler/approval/reporting paths.
5. **Test isolation risk:** ambient environment flags, especially LLM enablement, could reintroduce slow or real external behavior in tests.
6. **Artifact handling risk:** manifest/report optimization could read or embed artifact bodies instead of references/hashes only.
7. **Approval edge-case risk:** timeout, replay, hash mismatch, unauthorized actor, and denial semantics could regress.
8. **Over-refactor risk:** broad optimization could touch protected core or external systems unnecessarily.

## Mandatory Test Matrix

Before any Phase 9 implementation commit, the relevant subset and full suite must pass.

| Subsystem | Required tests |
|---|---|
| Sandbox boundary | `tests/sandbox`, `tests/security` |
| Approval/HITL | `tests/approval`, relevant `tests/telegram` approval paths |
| LLM safety/recovery | `tests/llm`, `tests/prompt_security` |
| Manifests/reporting | `tests/manifests`, `tests/reporting` |
| Session/memory | `tests/session`, `tests/memory` |
| Tool routing/scoping/skills | `tests/tool_routing`, `tests/tool_scoping`, `tests/skills` |
| Scheduler | `tests/scheduler` |
| Telegram mock/gated behavior | `tests/telegram` |
| Full regression | `python3 -m pytest tests -q --tb=short` |

Recommended Phase 9 validation order:

1. Targeted tests for touched module.
2. Cross-cutting safety subset:
   `python3 -m pytest tests/approval tests/llm tests/manifests tests/session tests/tool_scoping tests/telegram -q --tb=short`
3. Full suite:
   `python3 -m pytest tests -q --tb=short`
4. Secret/unsafe-output grep for changed files only.
5. `git status --short` to confirm no `external_sources/`, `.env`, tokens, or old untracked artifacts are staged.

## GO / NO-GO Criteria

### GO for Phase 9A

Phase 9A may start if:

- This plan is committed and pushed.
- Phase 8 closure report remains the baseline.
- Local branch is even with `origin/main`.
- No runtime/config/token files are modified.
- The initial Phase 9A scope is profiling/read-only/no behavior change.

### NO-GO for Phase 9A

Do not start Phase 9A if:

- Any full-suite test is failing.
- Any unreviewed runtime behavior change is present.
- `.env`, token, real Telegram, real LLM, CloudOps, or pentest changes are required.
- The work would touch Hermes runtime/code, Agent Zero, OpenCLAW, Qwen, TurboQuant, llama.cpp, or WSL2.
- The proposed work weakens R4/R5, approval checks, prompt security, tool scoping, manifests, scheduler dry-run, or SandboxController boundaries.

## Explicitly Prohibited in Phase 9 Planning

- No implementation changes in this planning step.
- No real Telegram execution.
- No real LLM calls.
- No real CloudOps execution.
- No real external pentest activity.
- No `.env` changes.
- No token changes or token printing.
- No runtime config changes.
- No SandboxController behavior changes.
- No approval execution boundary changes.
- No direct execution from approval success.
- No Hermes code copying.
- No Hermes code execution.
- No Hermes runtime/gateway/toolset integration.
- No broad refactor before Phase 9A profiling evidence.

## Proposed Subphases

### Phase 9A — Performance Profiling / No Behavior Change

**Goal:** Measure before optimizing.

Scope:

- Add profiling plans or read-only benchmark scripts only if explicitly approved in 9A.
- Identify hotspots in memory/context rendering, policy evaluation, report/manifest creation, LLM recovery, and Telegram mock flow.
- Produce profiling report without changing runtime behavior.

Acceptance criteria:

- No behavior changes.
- No real external execution.
- Profiling output redacted and reference-only where applicable.
- Full suite remains green.

### Phase 9B — Context and Memory Optimization

**Goal:** Reduce context/memory overhead while preserving safety.

Scope:

- Optimize redundant redaction/context rendering only after 9A evidence.
- Preserve non-authoritative compressed context.
- Preserve secret exclusion and R4/R5 no-downgrade semantics.

Acceptance criteria:

- `tests/memory`, `tests/session`, `tests/llm`, and full suite green.
- No secret leakage.
- PromptBuilder keeps recovered/compressed context as user-background only.

### Phase 9C — Policy Evaluation Optimization

**Goal:** Improve deterministic policy paths without changing decisions.

Scope:

- Optimize repeated normalization/classification only if decisions remain identical.
- Candidate paths: DangerousActionPolicy, PromptSecurity, MissionPolicy, ToolScopePolicy, SkillPolicy.

Acceptance criteria:

- Golden decision matrix proves no R4/R5 downgrade.
- `tests/policy`, `tests/prompt_security`, `tests/tool_scoping`, `tests/approval`, `tests/telegram`, and full suite green.

### Phase 9D — Reporting and Manifest Pipeline Optimization

**Goal:** Reduce duplicate redaction/rendering/hash work while preserving reference-only artifacts.

Scope:

- Optimize manifest/report construction without reading artifact bodies.
- Keep SHA-256/tamper validation and sensitive redaction requirements.

Acceptance criteria:

- `tests/manifests`, `tests/reporting`, and full suite green.
- Changed-file secret scan clean.
- No raw content/body metadata introduced.

### Phase 9E — Final Regression Hardening

**Goal:** Close Phase 9 with stronger regression coverage.

Scope:

- Consolidate golden tests for optimized paths.
- Update risk register, test summary, and optimization report.
- Confirm no runtime/config/external action drift.

Acceptance criteria:

- Full suite green.
- Security regression report updated.
- Phase 9 closure decision documented.

## Phase 9A Readiness Statement

**GO for Phase 9A planning/profiling only.**

Phase 9A should start as read-only profiling and no-behavior-change analysis. Any optimization implementation must wait for profiling evidence and must preserve Phase 8 safety invariants.
