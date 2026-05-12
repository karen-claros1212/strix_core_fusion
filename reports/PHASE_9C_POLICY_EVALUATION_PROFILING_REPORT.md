# Phase 9C Policy Evaluation Profiling Report

Date: 2026-05-12
Base commit: `311085fc2e2804893d0ef2a239e347d02372f389`
Scope: profiling/measurement/report only. No runtime optimization or policy behavior change was performed.

## Methodology

Baseline and validation commands:

```bash
python3 -m pytest tests/policy tests/security tests/approval tests/telegram -q
python3 -m pytest tests -q
```

Deterministic profiling was executed from a temporary script at `/tmp/strix_policy_profile.py` with `PYTHONPATH` pointed at this repository. The script used `time.perf_counter_ns()` over 7 rounds of 20,000 iterations per route and a `cProfile` pass over 5,000 repetitions of the complete route set. The temporary script asserted expected governed decisions before measuring.

Profiled routes:

- status/read benign
- repo audit dry-run
- create VPS/R4 approval_required
- delete server/R5 blocked
- prompt injection blocked
- approval valid
- approval hash mismatch
- tool route allowed
- unknown tool blocked
- sandbox allow/block
- fallback policy path

## Baseline Results

- Targeted policy/security/approval/telegram suite: `84 passed, 1 warning in 0.13s`
- Full suite: `359 passed, 3 warnings in 2.38s`

Warnings are the pre-existing coroutine-not-awaited warnings observed in integration/security tests; no warning count increase was introduced by profiling.

## Benchmark Results

| Route | Calls | Avg us/call | Fastest round avg us | Slowest round avg us | Stdev us | Decision marker |
|---|---:|---:|---:|---:|---:|---|
| status/read benign | 140,000 | 13.097 | 12.876 | 13.368 | 0.154 | `R0` |
| repo audit dry-run | 140,000 | 13.199 | 13.091 | 13.388 | 0.120 | `['sandbox', True, True]` |
| create VPS/R4 approval_required | 140,000 | 32.964 | 32.556 | 33.639 | 0.466 | `['R4', True, True, True]` |
| delete server/R5 blocked | 140,000 | 50.633 | 50.086 | 51.069 | 0.339 | `['R5', True, True, True]` |
| prompt injection blocked | 140,000 | 11.559 | 11.466 | 11.627 | 0.066 | `[False, 'block', ['ignore_previous_en', 'mission_policy_bypass']]` |
| approval valid | 140,000 | 6.365 | 6.302 | 6.434 | 0.044 | `[True, 'APPROVED']` |
| approval hash mismatch | 140,000 | 6.194 | 6.158 | 6.228 | 0.029 | `[False, 'INVALID_HASH']` |
| tool route allowed | 140,000 | 1.114 | 1.112 | 1.119 | 0.003 | `[True, 'direct_safe_metadata_only']` |
| unknown tool blocked | 140,000 | 13.191 | 13.016 | 13.279 | 0.112 | `[True, True, 'unknown_tool_blocked']` |
| sandbox allow/block | 140,000 | 7.323 | 7.187 | 7.407 | 0.073 | `[True, False, True, False, False]` |
| fallback policy path | 140,000 | 33.559 | 33.149 | 33.914 | 0.260 | `['R1', True, 'unknown_tool_blocked']` |

Fastest route: **tool route allowed** at `1.114` us/call average.

Slowest route: **delete server/R5 blocked** at `50.633` us/call average.

## Hotspots

Top cumulative `cProfile` excerpt:

```text
         7180002 function calls (7160002 primitive calls) in 2.538 seconds

   Ordered by: cumulative time
   List reduced from 140 to 25 due to restriction <25>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.026    0.026    2.643    2.643 strix_policy_profile.py:147(run_profiled_workload)
    20000    0.080    0.000    0.871    0.000 tool_scope_policy.py:20(decide)
    20000    0.031    0.000    0.847    0.000 mission_policy.py:10(classify_risk)
    40000    0.023    0.000    0.827    0.000 dangerous_action_policy.py:32(evaluate)
    40000    0.111    0.000    0.674    0.000 dangerous_action_detector.py:38(detect)
   830000    0.657    0.000    0.657    0.000 {method 'search' of 're.Pattern' objects}
    20000    0.032    0.000    0.531    0.000 tool_classifier.py:18(classify)
     5000    0.011    0.000    0.492    0.000 strix_policy_profile.py:61(delete_server_r5_blocked)
     5000    0.007    0.000    0.411    0.000 strix_policy_profile.py:98(fallback_policy_path)
     5000    0.011    0.000    0.394    0.000 strix_policy_profile.py:55(create_vps_r4_approval_required)
    10000    0.016    0.000    0.342    0.000 action_normalizer.py:41(canonicalize_action)
   110000    0.052    0.000    0.288    0.000 {built-in method builtins.any}
     5000    0.006    0.000    0.240    0.000 strix_policy_profile.py:85(unknown_tool_blocked)
    35000    0.011    0.000    0.233    0.000 action_normalizer.py:37(_matches)
     5000    0.004    0.000    0.227    0.000 strix_policy_profile.py:47(status_read_benign)
    10000    0.013    0.000    0.213    0.000 strix_policy_profile.py:33(make_approval)
     5000    0.007    0.000    0.212    0.000 strix_policy_profile.py:50(repo_audit_dry_run)
    20000    0.086    0.000    0.204    0.000 tool_scope_policy.py:61(_effective_scope)
   160000    0.032    0.000    0.204    0.000 action_normalizer.py:38(<genexpr>)
    10000    0.027    0.000    0.196    0.000 approval_request_builder.py:34(build)
     5000    0.020    0.000    0.180    0.000 strix_policy_profile.py:90(sandbox_allow_block)
   125000    0.033    0.000    0.172    0.000 __init__.py:173(search)
     5000    0.005    0.000    0.161    0.000 strix_policy_profile.py:71(approval_valid)
     5000    0.003    0.000    0.153    0.000 strix_policy_profile.py:67(prompt_injection_blocked)
     5000    0.009    0.000    0.150    0.000 prompt_security_layer.py:22(guard_for_llm)

```

Observed hotspots:

1. `ToolScopePolicy.decide` plus `ToolClassifier.classify` dominate combined scoped tool paths, especially repo-audit, unknown-tool, R4, and R5 routes.
2. `MissionPolicy.classify_risk` delegates to `DangerousActionPolicy.evaluate`, and `DangerousActionDetector.detect` spends most cumulative time in compiled regex searches.
3. `canonicalize_action` and `_matches` are visible in benign/fallback/R4 classification routes after dangerous-action screening.
4. Approval verification is comparatively fast; the measured cost includes deterministic in-memory request construction in the benchmark route.
5. Sandbox boundary checks are fast and mostly basic path/token validation.

## Safe Optimization Candidates

These are candidates for a later optimization phase only; none were implemented here.

- Reuse policy instances and registries where call sites create them repeatedly, while preserving evidence and deterministic decisions.
- Cache or short-circuit low-risk canonical action checks only after dangerous-action and prompt-injection checks remain authoritative.
- Avoid duplicate tool classification when a caller already provides authoritative classification metadata.
- Normalize tool scope context once per mission/workflow instead of per tool decision where the context is immutable.
- Keep compiled regex objects as they are; if optimizing, benchmark pattern ordering without weakening R4/R5 detection.

## Security-Critical Paths Not To Optimize Aggressively

- R5 destructive/cloud deletion/backup wipe classification and blocking.
- R4 cloud/resource creation approval-required path.
- Prompt injection / policy bypass / approval bypass detection.
- Unknown tool blocking and tool scope enforcement.
- Approval hash, expiry, user authorization, and replay checks.
- Sandbox boundary checks for path traversal, privileged Docker, destructive shell tokens, metadata endpoints, and blocked paths.

## Regression Risks For Optimization

- Reordering dangerous-action checks could accidentally downgrade R5 to R4/R1.
- Caching policy decisions without complete input/context keys could leak decisions across missions or approvals.
- Skipping scoped tool checks for known tools could reduce tool governance.
- Treating prompt-sanitized output as authoritative could bypass prompt policy decisions.
- Conflating sandbox dry-run allowance with execution allowance could widen capability beyond governed operation.

## Safety Confirmation

- Runtime files changed: **NO**
- R0/R1 read/analyze/report preserved: **YES**
- R2/R3 dry-run/sandbox preserved: **YES**
- R4 approval-required behavior preserved: **YES**
- R5 blocked behavior preserved: **YES**
- Tool routing, sandbox, approvals, and evidence behavior preserved: **YES**
- Real Telegram/real LLM/Qwen/TurboQuant/llama.cpp/Agent Zero/OpenCLAW/Hermes were not used: **YES**

## Final Validation Results

- Targeted policy/security/approval/telegram suite: `84 passed, 1 warning in 0.13s`
- Full suite: `359 passed, 3 warnings in 2.37s`

## GO/NO-GO

Verdict: **GO for Phase 9C Optimization**, provided optimization work remains constrained by the security-critical regression risks above and starts with tests that lock R4/R5, approval, prompt-injection, unknown-tool, and sandbox boundary behavior.
