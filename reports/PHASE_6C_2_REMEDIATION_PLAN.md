# PHASE 6C-2 REMEDIATION PLAN

## Scope
No patches are applied in Phase 6C-2. This plan classifies what can be safely fixed in a later phase and what needs review.

## Remediation Groups
### 6C2-5f2a13a2: Secret redaction implementation self-hit
- Root cause: `redaction-code-self-hit`
- Affected file/group: `saga_fusion/audit_logger.py`
- Recommended fix: Refine scanner to distinguish redaction patterns from real secrets; retain manual review for redaction code changes.
- Risk if not fixed: Operational noise and possible alert fatigue if left untriaged.
- Required tests: Run `python3 -m pytest tests/repo_audit -q --tb=short` and full suite after any scanner/report changes.
- Auto patch candidate: `False`
- Manual review required: `True`

### 6C2-1736e032: Historical report placeholder/diagnostic text flagged
- Root cause: `historical-report-secret-placeholder`
- Affected file/group: `reports/PHASE_6B_4_TELEGRAM_LLM_SMOKE_REPORT.md`
- Recommended fix: Keep audit history, but refine scanner to ignore already-redacted report text or mark as documentation drift.
- Risk if not fixed: Operational noise and possible alert fatigue if left untriaged.
- Required tests: Run `python3 -m pytest tests/repo_audit -q --tb=short` and full suite after any scanner/report changes.
- Auto patch candidate: `False`
- Manual review required: `True`

### 6C2-30938a19: Environment placeholder flagged as secret-like text
- Root cause: `env-example-placeholder`
- Affected file/group: `.env.example`
- Recommended fix: Keep placeholder blank; optionally refine scanner allowlist for .env.example keys.
- Risk if not fixed: Operational noise and possible alert fatigue if left untriaged.
- Required tests: Run `python3 -m pytest tests/repo_audit -q --tb=short` and full suite after any scanner/report changes.
- Auto patch candidate: `True`
- Manual review required: `False`

### 6C2-a9a5a159: Test config fixture flagged as insecure config
- Root cause: `test-config-fixtures`
- Affected file/group: `tests/repo_audit/test_repo_auditor.py`
- Recommended fix: Keep fixture; add fixture-aware classification to scanner.
- Risk if not fixed: Operational noise and possible alert fatigue if left untriaged.
- Required tests: Run `python3 -m pytest tests/repo_audit -q --tb=short` and full suite after any scanner/report changes.
- Auto patch candidate: `True`
- Manual review required: `False`

### 6C2-bcf76f36: Test secret fixture/redaction assertion flagged
- Root cause: `test-secret-fixtures`
- Affected file/group: `tests/llm/test_llm_config.py`
- Recommended fix: Keep test fixtures; ensure values are synthetic and scanner labels them as fixtures.
- Risk if not fixed: Operational noise and possible alert fatigue if left untriaged.
- Required tests: Run `python3 -m pytest tests/repo_audit -q --tb=short` and full suite after any scanner/report changes.
- Auto patch candidate: `False`
- Manual review required: `True`

## Phase Gate
Proceed to 6C-3 only after approving which P2/P3 scanner/report hygiene items should be patched.
