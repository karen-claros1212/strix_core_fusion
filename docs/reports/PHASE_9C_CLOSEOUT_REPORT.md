# Phase 9C Policy Evaluation Optimization Closeout Report

**Phase name:** Phase 9C Policy Evaluation Optimization  
**Date:** 2026-05-13  
**Git reference:** `f14ddb693f171f58f2dfc5f6103add92d6e73fcc` (`phase 9c: optimize policy evaluation paths`)  
**Closeout type:** Documentation-only closeout. No runtime behavior was changed by this report.

## Scope

Phase 9C optimized narrow policy evaluation paths identified by prior profiling while preserving existing security and governance semantics. The implementation stayed limited to policy evaluation internals and did not introduce new capabilities, external integrations, live execution paths, or policy relaxations.

This closeout records final validation, benchmark deltas, preserved invariants, and the formal GO/NO-GO boundary for follow-on work.

## Files Modified

Phase 9C implementation commit `f14ddb693f171f58f2dfc5f6103add92d6e73fcc` modified only these runtime policy-evaluation files:

- `saga_fusion/policy/dangerous_action_detector.py`
- `saga_fusion/policy/dangerous_action_policy.py`
- `saga_fusion/telegram/mission_policy.py`
- `saga_fusion/tool_routing/tool_classifier.py`
- `saga_fusion/tool_scoping/tool_scope_policy.py`

Phase 9C closeout documentation adds/updates documentation and status files only; it does not modify runtime code.

## Optimization Summary

- Added deterministic prefilter terms before expensive dangerous-action regex searches.
- Replaced repeated list membership checks with set-backed category/pattern checks where order-sensitive output remains preserved.
- Reduced intermediate string/list allocation in mission and tool request text construction.
- Avoided an unnecessary classification copy in tool-scope decisions.
- Short-circuited empty tool-scope contexts before evaluating optional scope sources.

The changes are micro-optimizations only. They do not alter R0-R5 classifications, approval requirements, dangerous-action categories, prompt-security outcomes, tool scope decisions, sandbox boundaries, redaction requirements, manifest behavior, or execution permissions.

## Benchmark Before/After

Local deterministic microbenchmark, 50,000 calls per route, 5 repeats, average microseconds per call. “Before” is the parent of `f14ddb693f171f58f2dfc5f6103add92d6e73fcc`; “After” is `f14ddb693f171f58f2dfc5f6103add92d6e73fcc`.

| Route | Before avg us/call | After avg us/call | Change |
|---|---:|---:|---:|
| status/read benign | 13.312 | 11.753 | -11.7% |
| repo audit dry-run | 16.190 | 8.731 | -46.1% |
| create VPS/R4 approval_required | 13.549 | 7.075 | -47.8% |
| delete server/R5 blocked | 21.282 | 12.724 | -40.2% |
| prompt injection blocked | 11.573 | 11.510 | -0.5% |
| unknown tool blocked | 14.373 | 8.307 | -42.2% |
| sandbox allow/block | 13.857 | 14.232 | +2.7% |

The benchmark is directional and local. Security behavior is authoritative; performance claims are limited to the deterministic test routes above.

## Validation Results

- Golden tests: `python3 -m pytest tests/policy/test_policy_evaluation_golden.py -q --tb=short` → `13 passed in 0.07s`.
- Targeted policy/security/approval/telegram: `python3 -m pytest tests/policy tests/security tests/approval tests/telegram -q` → `84 passed, 1 existing warning in 0.13s`.
- Full first-party suite: `python3 -m pytest tests -q` → `359 passed, 3 existing warnings in 2.36s`.

The warnings are the existing coroutine-not-awaited warnings already tracked in integration/security tests; Phase 9C did not introduce a warning-count increase.

## Security Invariants Preserved

- MissionPolicy remains authoritative for R0-R5 risk classification.
- PromptSecurity remains an early natural-language safety gate and does not become bypassable through optimized paths.
- R4 remains approval-required; R5 remains blocked/non-approvable.
- Approval hash, expiry, actor authorization, denial, and replay semantics remain unchanged.
- Tool routing and tool scoping still block unknown/out-of-scope tools and preserve sandbox/approval requirements.
- SandboxController remains the runtime boundary; dry-run allowance is not execution allowance.
- Redaction semantics and evidence metadata remain preserved.
- Manifest behavior remains non-authoritative and non-executable.
- No governed operational capability was widened or reduced.

## Explicitly Not Done

- No real Telegram execution.
- No real LLM execution.
- No CloudOps or external pentest execution.
- No Hermes code copied, imported, executed, or depended on.
- No direct execution path added.
- No R4/R5 semantic change.
- No capability reduction.
- No Agent Zero, OpenCLAW, Qwen, TurboQuant, llama.cpp, `.env`, token, or runtime configuration changes.

## GO/NO-GO

**GO:** Phase 9D planning only.

**NO-GO:** Any additional policy optimization without fresh profiling evidence and new golden coverage for the exact behavior being changed.

Phase 9C is closed. Follow-on work may plan Phase 9D, but further policy optimization requires new profiling, new golden behavior coverage, and explicit preservation of the security invariants above.
