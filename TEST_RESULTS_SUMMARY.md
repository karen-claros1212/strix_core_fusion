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
