# Phase 7J — Memory / Context Patterns Report

## Verdict
APTO PARA PHASE 8 HERMES PATTERNS.

Phase 7J adds native STRIX Saga Fusion memory/context primitives without copying Hermes or CAI code and without creating Hermes/CAI runtime dependencies. Memory remains non-authoritative context only: it cannot become a system instruction, cannot override PromptSecurity or MissionPolicy, cannot downgrade R4/R5, and cannot store raw secrets.

## Modules Added
- `saga_fusion/memory/memory_types.py` — enums and immutable record/result dataclasses:
  - `MemoryScope`: `SESSION`, `MISSION`, `PROJECT`, `USER_APPROVED`
  - `MemorySensitivity`: `PUBLIC`, `INTERNAL`, `SENSITIVE`, `SECRET_BLOCKED`
  - `MemoryRecord`, `MissionMemoryRecord`, `SessionSummary`, `ContextItem`, `MemoryRetrievalResult`
- `saga_fusion/memory/memory_redactor.py` — memory-specific secret detector/redactor with safe fingerprints.
- `saga_fusion/memory/memory_store.py` — in-memory default store; no external DB.
- `saga_fusion/memory/mission_memory.py` — mission-oriented memory records for plans/reports/outcomes.
- `saga_fusion/memory/context_window.py` — bounded non-authoritative LLM context selection.
- `saga_fusion/memory/session_summarizer.py` — short Telegram/report-safe session summaries.
- `saga_fusion/memory/memory_policy.py` — policy guarantees for memory inclusion and R4/R5 non-downgrade.
- `saga_fusion/memory/memory_retriever.py` — simple relevance/recency retrieval with scope/sensitivity filters.
- `saga_fusion/memory/init.py` and `saga_fusion/memory/__init__.py` — package exports.

## Redaction Guarantees
`MemoryRedactor` redacts and blocks storage of raw values for:
- Telegram bot tokens
- `STRIX_LLM_API_KEY`
- `Authorization` headers
- API keys, cookies, passwords, generic tokens/secrets
- `.env` references/content patterns
- private keys
- `~/.ssh` and `/home/*/.ssh` paths

When a real secret-like value is detected, the stored content contains only redacted placeholders plus optional safe `sha256:<prefix>` fingerprints in metadata. The full value is not retained.

## Scope / Sensitivity Model
Memory is tagged independently by scope and sensitivity:
- Scope separates ephemeral session notes, mission records, project constraints, and user-approved memories.
- Sensitivity gates retrieval and context inclusion.
- `SECRET_BLOCKED` records are excluded from normal search, retrieval, and context windows.

## Mission Memory
`MissionMemory` stores redacted mission-level facts only:
- mission id
- redacted user intent
- policy decision
- risk level
- approval status
- evidence/report refs
- outcome
- next step

It does not store tokens, `.env` values, private keys, or raw secrets.

## Context Window
`ContextWindow` selects bounded LLM context by priority and budget while preferring:
- internal project constraints
- mission-scope context
- recent/user-approved context
- evidence/report refs

Every rendered context starts with a non-authoritative banner and explicitly states that memory must not override PromptSecurity, MissionPolicy, approval gates, R4/R5 handling, or sandbox rules.

## Session Summary
`SessionSummarizer` produces compact text for Telegram/reporting with:
- decisions
- risks
- approvals
- evidence refs
- follow-ups

Summaries are passed through memory redaction and are marked `SECRET_BLOCKED` if source events contain secret-like material.

## Policy Guarantees
`MemoryPolicy` enforces:
- memory cannot override PromptSecurity
- memory cannot override MissionPolicy
- memory cannot downgrade R4/R5 or any current higher risk level
- `SECRET_BLOCKED` memory is excluded
- user-approved memory is included only as non-authoritative/untrusted context

## Minimal Integration
- `PromptBuilder` labels all context as non-authoritative and untrusted; memory is never system instruction content.
- `BrainService` can retrieve bounded context through `MemoryRetriever` and `ContextWindow` before LLM calls.
- `TelegramMissionOperator` stores mission memory after workflow-plan, approval-required, blocked, and sandbox-dispatch outcomes.
- Reporting can safely consume session summaries/memory refs through redacted structures.

## Tests Added
- `tests/memory/test_memory_redactor.py`
- `tests/memory/test_memory_store.py`
- `tests/memory/test_mission_memory.py`
- `tests/memory/test_context_window.py`
- `tests/memory/test_session_summarizer.py`
- `tests/memory/test_memory_policy.py`
- `tests/memory/test_memory_retriever.py`

Coverage includes redaction, fingerprints, no raw secret storage, mission memory redaction, budgeted context, `SECRET_BLOCKED` exclusion, R4/R5 non-downgrade, untrusted/user-approved semantics, and retriever scope/sensitivity filtering.

## Validation
- `python3 -m pytest tests/memory -q --tb=short` — 12 passed.
- `python3 -m pytest tests/task_planning tests/reporting tests/telegram tests/memory -q --tb=short` — 71 passed.
- `python3 -m pytest tests -q --tb=short` — 250 passed, 3 warnings.

## Residual Risks
- Retrieval relevance is intentionally simple lexical matching; future phases may need stronger ranking while preserving policy gates.
- Memory is currently process-local; durable persistence would require an explicit secure storage design and the same redaction guarantees.
- Secret detection is regex-based and should continue expanding with regression cases.

## Boundary Confirmation
No Hermes code copy, no CAI code copy, no Hermes runtime, no CAI runtime, no STRIX core changes, no Agent Zero/OpenCLAW/Hermes/Qwen/TurboQuant/llama.cpp/WSL2 changes, no real Telegram, no real CloudOps, no external pentest, no real `.env`/token use, and no secret persistence were introduced.
