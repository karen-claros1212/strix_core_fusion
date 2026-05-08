# TEST RESULTS SUMMARY

## Phase 6B-3 Validation
Date: 2026-05-07  
Root: `/mnt/Proyectos/strix_core_fusion`

### Commands
- `python3 -m pytest tests/telegram -q --tb=short`
- `python3 -m pytest tests/sandbox tests/telegram tests/unit -q --tb=short`
- `python3 -m pytest tests -q --tb=short`

### Results
- Telegram suite: 42 passed, 0 failed
- Core subset (`tests/sandbox tests/telegram tests/unit`): 117 passed, 0 failed
- Full suite: 141 passed, 0 failed, 3 warnings

### Warnings
- 3 existing coroutine-not-awaited warnings in integration/security tests.
- No Phase 6B-3 test failures.

### Coverage Added/Updated
- Real mode without token blocks startup.
- Real mode without allowed users blocks startup.
- Mock mode does not require token.
- Token does not appear in logs.
- Unauthorized user denied.
- R4 generates `approval_required` with `action_hash`.
- R5 is blocked.
- Replay guard blocks reused callback/action hashes.
- Action hash mismatch blocks approval.
- Mock mode flow remains green.
- Tests avoid real Telegram API calls.


## Test Results (Phase 6B-4)
- LLM + Telegram: 52 passed
- Sandbox + Telegram + LLM + Unit: 127 passed
- Full suite: 151 passed, 3 warnings
- New LLM tests cover config gating, payload construction, timeout handling, no-tool-execution brain service, router fallbacks, and Telegram natural-language mocked brain flow.


## Test Results (Phase 6B-4B)
- LLM + Telegram normalization suite: 64 passed
- Full suite: 163 passed, 3 warnings
- Added tests for ES/EN R4 infra changes, R5 destructive deletes, benign status/audit text, and highest-risk-wins conflicts.


## Test Results (Phase 6C-1)
- Repo audit + LLM + Telegram: 66 passed
- Full suite: 165 passed, 3 warnings
- Added tests for dry-run repo auditor secret redaction, Docker/config findings, evidence/report rendering.


## Test Results (Phase 6C-2)
- Repo audit tests: 4 passed
- Full suite: 167 passed, 3 warnings
- Added tests for finding triage deduplication and .env.example placeholder handling.


## Test Results (Phase 6C-3)
- Repo audit tests: 6 passed
- Full suite: 169 passed, 3 warnings
- Added regression tests for `.env.example` safe placeholders and test-fixture config audit suppression.


## Test Results (Phase 6C-4)
- Repo audit tests: 6 passed
- Full suite: 169 passed, 3 warnings
- No functional code changes were applied in this phase.


## Test Results (Phase 6C-5)
- Repo audit tests: 10 passed
- Full suite: 173 passed, 3 warnings
- Added tests for redaction self-reference classification, real runtime secret detection, synthetic test fixture classification, and historical evidence placeholder classification.


## Test Results (Phase 6C-6)
- Repo audit tests: 10 passed
- Full suite: 173 passed, 3 warnings
- No functional code changes were applied in final re-audit.


## Test Results (Phase 7A)
- Full suite: 173 passed, 3 warnings
- Phase 7A applies documentation/source-audit changes only.


## Test Results (Phase 7B)
- Full suite: 173 passed, 3 warnings
- Phase 7B is documentation/planning only.


## Test Results (Phase 7C)
- Prompt security tests: 12 passed
- LLM + Telegram + PromptSecurity tests: 76 passed
- Full suite: 185 passed, 3 warnings
- Added tests for ALLOW/WARN/BLOCK/ESCALATE, pre-LLM blocking, mock mode, R4 approval, and R5 blocking regressions.
