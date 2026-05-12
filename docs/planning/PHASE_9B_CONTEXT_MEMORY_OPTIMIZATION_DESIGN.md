# STRIX Phase 9B Context-Memory Optimization Design

**Project:** STRIX ELITE CYBER AGENT  
**Phase:** 9B — Context and Memory Optimization Design  
**Document type:** Planning/design only; no optimization implementation  
**Created:** 2026-05-12  
**Baseline:** `61e052e phase 9a: add profiling report`  
**Last full validation baseline:** 334 passed / 0 failed / 3 existing warnings

## Executive Summary

Phase 9A identified `ContextCompressor.compress` as the strongest Phase 9B optimization candidate: approximately **2.45ms per 200 context items** in deterministic local profiling. Phase 9B must not optimize directly yet. The correct next step is to define golden behavior tests and a narrow optimization design that preserves security semantics exactly.

The target path lives in `saga_fusion/session/compressor.py`. Its current cost comes from per-item extraction, dataclass conversion, redaction, instruction neutralization, string prefixing, join/truncation, and metadata accounting.

## Current Behavior of `ContextCompressor.compress`

Current implementation summary:

1. Resolve `budget_chars` from `SessionRecoveryPolicy.default_budget_chars` unless explicit.
2. Normalize input to a sequence: lists/tuples/sets are iterated; single values become one item.
3. Skip `None` items.
4. Exclude items with `sensitivity == MemorySensitivity.SECRET_BLOCKED`.
5. Extract text by type:
   - `CompressedContext` → `.text`
   - `SessionSummary` → `.text`
   - `ContextItem` → `.content`
   - `dict` → `content`, `text`, `summary`, `user_intent`, or stringified dict
   - dataclass → `asdict()` then `content`, `text`, or stringified payload
   - fallback → `str(item)`
6. Count `original_chars` before redaction.
7. Apply `MemoryRedactor.redact_text`.
8. If redactor marks `secret_blocked`, exclude the item and set `redacted=True`.
9. Neutralize instruction-like text via `neutralize_instruction_text`.
10. Append non-empty output as `[UNTRUSTED_QUOTED_CONTEXT] ...`.
11. Join rendered lines with newline separators.
12. If over budget, truncate and append `[TRUNCATED_TO_CONTEXT_BUDGET]` when budget permits.
13. Return `CompressedContext` with:
    - `non_authoritative=True`
    - `execution_allowed=False`
    - budget/original/compressed/truncated/redacted/excluded metadata.

## Invariants That Cannot Change

1. **Non-authoritative context:** output must always set `non_authoritative=True`.
2. **No execution:** output must always set `execution_allowed=False`.
3. **Secret exclusion:** `MemorySensitivity.SECRET_BLOCKED` and redactor `secret_blocked` items must be excluded, not summarized.
4. **Redaction semantics:** redaction markers and sensitive-value removal must remain identical or stricter.
5. **Instruction neutralization:** system/developer/policy-bypass instruction text must remain neutralized and quoted as untrusted context.
6. **R4/R5 no-downgrade:** compressed/recovered context must not alter MissionPolicy or approval decisions.
7. **Order preservation:** rendered output must preserve the original eligible item order for ordered inputs.
8. **Budget semantics:** truncation must occur only after rendering and must preserve the existing truncation marker behavior.
9. **Metadata semantics:** `budget_chars`, `original_chars`, `compressed_chars`, `truncated`, `redacted`, and `excluded_secret_count` must remain equivalent.
10. **No external reads:** compression must not read `.env`, tokens, real LLM, real Telegram, files, network, CloudOps, or external targets.

## Risks of Information Loss

- Skipping stringification or dataclass conversion could lose fallback content used today.
- Early truncation before redaction/neutralization could hide secret-bearing content from redaction logic.
- De-duplicating similar entries could remove evidence chronology or approval constraints.
- Changing dictionary field precedence could alter user intent/context selection.
- Dropping empty-after-neutralization items is valid today; changing that rule could add noise.

## Risks of Altering Order / Context Priority

- `compress` currently preserves iteration order for lists/tuples and whatever iteration order is supplied by sets. Optimizations must not sort or rank items inside `compress`.
- Priority selection belongs to `ContextWindow`, not `ContextCompressor`.
- Any batching/cache strategy must preserve rendered item order exactly.
- Caching extracted text by object identity is risky if mutable dicts/dataclasses are changed between calls.

## Risks of Reducing Redaction / Security Metadata

- Avoiding repeated `MemoryRedactor.redact_text` may leak secrets unless the cached value includes redaction status and is invalidated safely.
- Optimizing away `neutralize_instruction_text` could allow system/developer instruction injection into recovered context.
- Treating already-compressed context as trusted would violate Phase 8F safety; it must remain untrusted quoted context.
- Changing `redacted_any` semantics could hide that secret-bearing items were excluded.
- Changing `excluded_secret_count` semantics could weaken auditability.

## Edge Cases to Preserve

- Empty input and `None` input.
- Empty list/tuple/set input.
- Single string input.
- Dicts with `content`, `text`, `summary`, and `user_intent` precedence.
- Dataclass payloads with and without `content`/`text` fields.
- `ContextItem` with `SECRET_BLOCKED` sensitivity.
- Redactor-detected secret values inside otherwise normal strings.
- Instruction-injection text such as system/developer override requests.
- Very small `budget_chars`, including zero.
- Exact budget boundary and over-budget truncation.
- Ordered repeated items.
- Existing `CompressedContext` used as input.

## Proposed Golden Behavior Tests

These tests should be added before or alongside any 9B implementation patch.

| Test | Purpose | Expected invariant |
|---|---|---|
| `test_compress_empty_input_golden` | Empty/None context | Empty text, zero/known counts, non-authoritative, non-executing. |
| `test_compress_small_input_no_truncation_golden` | Small normal strings | Existing untrusted prefix, no truncation, order preserved. |
| `test_compress_large_input_truncates_golden` | Over-budget input | Current truncation marker and budget behavior preserved. |
| `test_compress_preserves_order_golden` | Ordered multi-item list | Rendered item order unchanged. |
| `test_compress_preserves_metadata_counts_golden` | Original/compressed/excluded/redacted counts | Metadata matches current behavior. |
| `test_compress_redaction_and_secret_exclusion_golden` | Secret-like content and `SECRET_BLOCKED` item | Secret excluded/redacted; no raw secret in output. |
| `test_compress_instruction_neutralization_golden` | System/developer/bypass text | Output remains untrusted and neutralized. |
| `test_compress_budget_zero_and_boundary_golden` | Soft/hard boundary behavior | Existing marker and empty budget behavior preserved. |
| `test_compress_deterministic_repeated_calls_golden` | Same input repeated | Identical `CompressedContext.to_dict()` except no time-varying fields. |
| `test_compress_no_env_or_real_io_golden` | Monkeypatch env/file/network/LLM access if applicable | Compressor does not read `.env`, call LLM, or touch Telegram. |

Recommended location: `tests/session/test_context_compressor_golden.py`.

## Proposed Deterministic Microbenchmarks

Benchmarks should be local-only, deterministic, and excluded from normal runtime behavior.

1. `ContextCompressor.compress` with 10, 50, 200, 500 context items.
2. Mix of strings, dicts, `ContextItem`, `SessionSummary`, and dataclasses.
3. Secret-bearing inputs to measure exclusion/redaction path separately.
4. Instruction-injection text to measure neutralization path separately.
5. Budget values: 0, 512, 4096, default.
6. Repeated-call benchmark to evaluate cache candidates only after golden tests exist.

Benchmarks must not:

- read `.env`;
- call real LLM;
- call real Telegram;
- touch CloudOps/pentest;
- print secrets;
- write runtime configs.

## Narrow Optimization Design Candidates

Only consider these after golden tests are committed and green.

### Candidate A — Fast path for already-safe primitive strings

Potential approach:

- Avoid extra dataclass/dict checks once item type is known as `str`.
- Still run redaction and instruction neutralization.

Risk:

- Low, if redaction and neutralization remain mandatory.

### Candidate B — Local helper split for extraction/redaction/rendering

Potential approach:

- Extract pure helpers: `_iter_context_items`, `_render_safe_item`, `_truncate_to_budget`.
- No behavior change; enables targeted tests and future micro-optimization.

Risk:

- Medium, because helper extraction can subtly alter metadata/order/truncation.

### Candidate C — Avoid `asdict()` unless needed

Potential approach:

- For dataclasses, check direct attributes `content`/`text` before full `asdict()` conversion.

Risk:

- Medium, because fallback string representation may change for dataclasses without those fields.

### Candidate D — Join/truncation budget-aware rendering

Potential approach:

- Track rendered length while appending to reduce final oversize string allocation.
- Must still account for `original_chars`, redaction, neutralization, and exclusion for all items.

Risk:

- High if implemented incorrectly, because early stopping could skip redaction/exclusion accounting for later items.

## Changes Prohibited in 9B

- Do not skip `MemoryRedactor.redact_text`.
- Do not skip `neutralize_instruction_text`.
- Do not make compressed context authoritative.
- Do not set or allow `execution_allowed=True`.
- Do not reorder context items inside `compress`.
- Do not let compressed context alter R4/R5 decisions.
- Do not read `.env`, tokens, files, network, real LLM, or real Telegram.
- Do not change SandboxController, ApprovalVerifier, MissionPolicy, or Telegram real runtime behavior.
- Do not copy or execute Hermes code.
- Do not introduce global mutable caches for context data.
- Do not implement optimization before golden tests are green.

## Required Test Matrix for 9B Implementation

Minimum tests before any optimization commit:

1. New golden compressor tests in `tests/session/test_context_compressor_golden.py`.
2. Existing session tests: `python3 -m pytest tests/session -q --tb=short`.
3. Memory/security tests: `python3 -m pytest tests/memory tests/security -q --tb=short`.
4. LLM/prompt safety tests: `python3 -m pytest tests/llm tests/prompt_security -q --tb=short`.
5. Full suite: `python3 -m pytest tests -q --tb=short`.
6. Changed-file secret scan for any modified source/tests/reports.

## GO / NO-GO Criteria for Implementing 9B

### GO

Implementation may start only if:

- Golden behavior tests are added and fail/pass against current behavior as expected.
- No production/runtime/security behavior changes are needed to add the tests.
- The proposed optimization targets only `ContextCompressor` or tiny local helpers.
- All relevant tests pass before and after the optimization.
- The output `CompressedContext.to_dict()` remains identical for golden fixtures.

### NO-GO

Do not implement 9B optimization if:

- Golden tests are missing.
- Any R4/R5, approval, prompt security, sandbox, LLM recovery, or manifest invariant must change.
- Optimization requires real LLM/Telegram/CloudOps/pentest calls.
- Optimization requires `.env`, token, runtime config, or external source changes.
- Optimization requires broad refactoring outside context/session/memory helpers.

## 9B Readiness Verdict

**GO for adding golden behavior tests.**

**CONDITIONAL GO for a narrow `ContextCompressor.compress` optimization only after those tests are committed and green.**

**NO-GO for direct optimization without golden behavior tests.**
