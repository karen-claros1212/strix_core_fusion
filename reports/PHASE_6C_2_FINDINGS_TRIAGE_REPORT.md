# PHASE 6C-2 FINDINGS TRIAGE REPORT

## Executive Summary
- Source findings: 35
- Deduplicated findings/groups: 5
- CRITICAL: 0
- HIGH: 0
- MEDIUM: 0
- LOW: 1
- INFO: 4

## Priority Matrix
- P0: 0
- P1: 0
- P2: 1
- P3: 4

## Auto-fix / Manual Review
- Auto-fix safe: 2
- Requires manual review: 3

## Normalized Findings
### 6C2-5f2a13a2: Secret redaction implementation self-hit
- File: `saga_fusion/audit_logger.py:39`
- Category: `secret_scan`
- Type: `logging/evidence leakage`
- Severity: `LOW`
- Priority: `P2`
- Confidence: `HIGH`
- Exploitability: `LOW`
- Impact: `LOW`
- Remediation complexity: `LOW`
- False-positive likelihood: `MEDIUM`
- Source count: `7`
- Evidence: `(r'(?i)api[_-]?key\s*[=:]\s*([a-zA-Z0-9_-]+)', r'api_key=[REDACTED]`
- Recommended action: Refine scanner to distinguish redaction patterns from real secrets; retain manual review for redaction code changes.
- Auto-fix safe: `False`
- Requires manual review: `True`

### 6C2-1736e032: Historical report placeholder/diagnostic text flagged
- File: `reports/PHASE_6B_4_TELEGRAM_LLM_SMOKE_REPORT.md:11`
- Category: `secret_scan`
- Type: `documentation drift`
- Severity: `INFO`
- Priority: `P3`
- Confidence: `MEDIUM`
- Exploitability: `NONE`
- Impact: `LOW`
- Remediation complexity: `LOW`
- False-positive likelihood: `HIGH`
- Source count: `5`
- Evidence: `- Chat completion via OpenAI-compatible client: FAIL, `http_error` (server returned auth error for configured `STRIX_LLM_API_KEY=[REDACTED]`
- Recommended action: Keep audit history, but refine scanner to ignore already-redacted report text or mark as documentation drift.
- Auto-fix safe: `False`
- Requires manual review: `True`

### 6C2-30938a19: Environment placeholder flagged as secret-like text
- File: `.env.example:14`
- Category: `secret_scan`
- Type: `secret handling`
- Severity: `INFO`
- Priority: `P3`
- Confidence: `HIGH`
- Exploitability: `NONE`
- Impact: `LOW`
- Remediation complexity: `LOW`
- False-positive likelihood: `HIGH`
- Source count: `1`
- Evidence: `STRIX_LLM_API_KEY=[REDACTED]`
- Recommended action: Keep placeholder blank; optionally refine scanner allowlist for .env.example keys.
- Auto-fix safe: `True`
- Requires manual review: `False`

### 6C2-a9a5a159: Test config fixture flagged as insecure config
- File: `tests/repo_audit/test_repo_auditor.py:8`
- Category: `config_audit`
- Type: `weak test coverage`
- Severity: `INFO`
- Priority: `P3`
- Confidence: `HIGH`
- Exploitability: `NONE`
- Impact: `LOW`
- Remediation complexity: `LOW`
- False-positive likelihood: `HIGH`
- Source count: `2`
- Evidence: `(tmp_path / "config.ini").write_text("debug=true\n")`
- Recommended action: Keep fixture; add fixture-aware classification to scanner.
- Auto-fix safe: `True`
- Requires manual review: `False`

### 6C2-bcf76f36: Test secret fixture/redaction assertion flagged
- File: `tests/llm/test_llm_config.py:24`
- Category: `secret_scan`
- Type: `weak test coverage`
- Severity: `INFO`
- Priority: `P3`
- Confidence: `HIGH`
- Exploitability: `NONE`
- Impact: `LOW`
- Remediation complexity: `LOW`
- False-positive likelihood: `HIGH`
- Source count: `20`
- Evidence: `cfg = LLMConfig(enabled=True, base_url='http://127.0.0.1:8080/v1', model='qwen', api_key=[REDACTED]`
- Recommended action: Keep test fixtures; ensure values are synthetic and scanner labels them as fixtures.
- Auto-fix safe: `False`
- Requires manual review: `True`
