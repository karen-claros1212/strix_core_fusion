# Phase 8H — LLM Error Taxonomy + Recovery Report

Date: 2026-05-12
Base: `10b85c5` (Phase 8G)

## Scope
Implemented a clean-room Saga Fusion LLM error taxonomy and bounded recovery layer for local OpenAI-compatible gateway resilience. This phase does not introduce real LLM calls in tests, tool execution, provider fallback, credential rotation, Hermes runtime/code, or Qwen/TurboQuant/llama.cpp/WSL2 changes.

## Components
- `saga_fusion/llm/error_types.py`
  - `LLMErrorCategory`: auth, timeout, connection, rate_limit, server_error, invalid_response, unsafe_output, context_too_large, model_unavailable, unknown.
  - `LLMErrorSeverity`, `LLMErrorRecord`, `LLMRecoveryDecision` with serializable metadata.
- `saga_fusion/llm/error_classifier.py`
  - Maps response errors/status/exception strings to categories.
  - Redacts Bearer tokens, OpenAI-style `sk-*` keys, API keys, tokens, secrets, and authorization assignments in evidence.
  - Detects unsafe LLM output patterns that attempt tool execution or policy/sandbox bypass.
- `saga_fusion/llm/recovery_policy.py`
  - Explicit bounded retry limits: default max 2, category-specific retry caps.
  - Retryable: timeout, connection, rate limit, server error.
  - Nonretryable: auth, invalid response, unsafe output, context too large, model unavailable, unknown.
  - Backoff is metadata only; no sleep or direct action.
- `saga_fusion/llm/recovery_manager.py`
  - Executes only the supplied LLM client call with explicit bounded retry count.
  - Records recovery history and last decision; no tools, shell, gateway switching, or unbounded loops.
- `BrainService` / `LLMRouter`
  - Integrates recovery metadata on failures.
  - Returns deterministic safe fallback missions when recovery falls back.
  - Marks routed missions `executed=False` and preserves existing public APIs.
  - Invalid JSON and unsafe output are classified and surfaced as `llm_recovery` metadata.
- `tests/llm/conftest.py`
  - Forces `STRIX_LLM_ENABLED=false` for tests so developer shell LLM env vars cannot trigger live gateway calls. Enabled LLM paths are tested only with explicit stub configs/clients.

## Security Gates
- No Hermes code copy, execution, runtime, gateway, or toolset usage.
- No Agent Zero/OpenCLAW/Qwen/TurboQuant/llama.cpp/WSL2 changes.
- No real Telegram, CloudOps, external pentest, tokens, or `.env` changes.
- No direct execution introduced; fallback is deterministic and non-executing.
- Retry limits are explicit; max-retry exhaustion stops and falls back safely.
- Auth/context/model/invalid/unsafe errors are nonretryable.
- R4/R5 fallback risk is preserved via existing canonicalizer/MissionPolicy highest-risk behavior.
- PromptSecurity, MissionPolicy, ApprovalVerifier, ToolRouter, and SandboxController remain authoritative.
- Error evidence redacts API keys and Bearer tokens.

## Tests
- `python3 -m pytest tests/llm -q --tb=short` → `31 passed in 0.07s`
- `python3 -m pytest tests/llm tests/prompt_security tests/session -q --tb=short` → `55 passed in 0.09s`
- `python3 -m pytest tests -q --tb=short` → `327 passed, 3 warnings in 2.35s`

Warnings are the pre-existing coroutine warnings in integration/security tests.

## Verdict
Phase 8H is complete and ready for Phase 8I Approval Timeout + Regression Depth. The LLM resilience layer is taxonomy/reporting-first, bounded, non-executing, redacted, and does not weaken R4/R5 or existing STRIX safety authorities.
