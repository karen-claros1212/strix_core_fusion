# PHASE 3 FIX PLAN

## Overview
Phase 3 execution revealed 18 critical issues (10 failed, 8 errors) out of 38 tests. The architecture is sound, but implementation details need correction.

## Priority 1: Critical Errors (Setup/Integration)
1.  **`strix_adapter.py` - Null State**
    *   **Issue**: `AttributeError: 'NoneType' object has no attribute 'get_conversation_history'` in `UnifiedSagaAgent`.
    *   **Fix**: Ensure `state` is initialized before `_setup_fusion_hooks` is called in `__init__`.
2.  **`tool_guard.py` - Signature Mismatch**
    *   **Issue**: Tests expect `SagaToolGuard()` but `__init__` requires `policy` and `logger`.
    *   **Fix**: Update tests to pass mocked `policy` and `logger` instances, or provide defaults in `__init__`.

## Priority 2: Failed Tests (Logic/Regex)
1.  **`audit_logger.py` - Regex Error**
    *   **Issue**: `re.PatternError: invalid group reference 1`.
    *   **Fix**: Patterns like `~/.ssh` lack capturing groups `()`. Change replacement string from `\1[REDACTED]` to `[REDACTED]` or add groups `(~/.ssh)`.
2.  **`audit_logger.py` - Missing Method**
    *   **Issue**: Tests call `log_decision(decision)` but signature is `log_decision(decision, action)`.
    *   **Fix**: Update tests or signature to match.
3.  **`security_policy.py` - Severity Mismatch**
    *   **Issue**: `test_denylist` expects `HIGH` but gets `MEDIUM`.
    *   **Fix**: Ensure denylist matches return `severity="HIGH"`.

## Priority 3: Minor Fixes
1.  **`test_saga_fusion.py` - Missing Method**
    *   **Issue**: Calls `_redact` which doesn't exist (should be `redact_secrets`).
    *   **Fix**: Update test method call.

## Execution Strategy
1.  Fix `audit_logger.py` regex patterns.
2.  Fix `tool_guard.py` test initialization.
3.  Fix `strix_adapter.py` state initialization.
4.  Re-run full test suite.
