# PHASE 6C-1 STRIX CORE REPOSITORY AUDIT DRY-RUN REPORT

## Executive Summary
STRIX repository audit executed in dry-run mode against the local STRIX repo as lab target. No production/external target was touched and no patches were applied.

## Scope
- Repo root: `/mnt/Proyectos/strix_core_fusion`
- Generated UTC: `2026-05-08T00:53:37.041162Z`
- Mode: `dry_run`
- Evidence: `reports/evidence/repo_audit_6c1_a891620db8fd9212.json`

## Inventory
- Files scanned: 182
- Python files: 106
- Docker/Compose files: 0
- Import references: 396

## Findings Summary
- HIGH: 33
- MED: 0
- LOW: 2

## Dependency Import Topology
- `saga_fusion`: 108
- `typing`: 25
- `os`: 17
- `pytest`: 17
- `unittest`: 16
- `json`: 14
- `dataclasses`: 12
- `logging`: 11
- `re`: 11
- `datetime`: 10
- `strix`: 10
- `pathlib`: 8
- `telegram_types`: 8
- `sandbox_types`: 7
- `enum`: 6
- `hashlib`: 6
- `time`: 6
- `urllib`: 5
- `uuid`: 5
- `asyncio`: 4
- `llm_config`: 4
- `subprocess`: 4
- `telegram_security`: 4
- `command_parser`: 3
- `sys`: 3

## Findings
### 1. [HIGH] Potential secret pattern: api_key_assignment
- Category: `secret_scan`
- Location: `.env.example:14`
- Evidence: `STRIX_LLM_API_KEY=[REDACTED]`
- Recommendation: Move secrets to runtime env and keep only placeholders in repo.

### 2. [HIGH] Potential secret pattern: api_key_assignment
- Category: `secret_scan`
- Location: `reports/PHASE_6B_4_TELEGRAM_LLM_SMOKE_REPORT.md:11`
- Evidence: `- Chat completion via OpenAI-compatible client: FAIL, `http_error` (server returned auth error for configured `STRIX_LLM_API_KEY=[REDACTED]`
- Recommendation: Move secrets to runtime env and keep only placeholders in repo.

### 3. [HIGH] Potential secret pattern: api_key_assignment
- Category: `secret_scan`
- Location: `reports/PHASE_6B_4_TELEGRAM_LLM_SMOKE_REPORT.md:64`
- Evidence: `- Model endpoint is visible from container via `host.docker.internal`, but chat completion fails with auth error for the configured `STRIX_LLM_API_KEY=[REDACTED]`
- Recommendation: Move secrets to runtime env and keep only placeholders in repo.

### 4. [HIGH] Potential secret pattern: api_key_assignment
- Category: `secret_scan`
- Location: `reports/PHASE_6B_3_PREFLIGHT_CHECKLIST.md:7`
- Evidence: `- [x] No real API keys in source (test-only `api_key=[REDACTED] and `token123` present in test asserts)`
- Recommendation: Move secrets to runtime env and keep only placeholders in repo.

### 5. [HIGH] Potential secret pattern: api_key_assignment
- Category: `secret_scan`
- Location: `reports/PHASE_6B_1C_FAILURE_CLASSIFICATION.md:28`
- Evidence: `| `tests/telegram/test_telegram_mission_operator.py` | `test_evidence_log_redacts_secrets` | `AssertionError: assert 'REDACTED' in 'api_key=[REDACTED] | 5. Error real de lógica | `EvidenceLogger` | Corregir código |`
- Recommendation: Move secrets to runtime env and keep only placeholders in repo.

### 6. [HIGH] Potential secret pattern: api_key_assignment
- Category: `secret_scan`
- Location: `reports/PHASE_6B_4_LLM_AUTH_DIAG_REPORT.md:43`
- Evidence: `2. Set it only in runtime env, for example `/ductor/.env`, as `STRIX_LLM_API_KEY=[REDACTED] llama-server key>`.`
- Recommendation: Move secrets to runtime env and keep only placeholders in repo.

### 7. [HIGH] Potential secret pattern: api_key_assignment
- Category: `secret_scan`
- Location: `tests/llm/test_llm_config.py:24`
- Evidence: `cfg = LLMConfig(enabled=True, base_url='http://127.0.0.1:8080/v1', model='qwen', api_key=[REDACTED]`
- Recommendation: Move secrets to runtime env and keep only placeholders in repo.

### 8. [HIGH] Potential secret pattern: api_key_assignment
- Category: `secret_scan`
- Location: `tests/repo_audit/test_repo_auditor.py:5`
- Evidence: `(tmp_path / "app.py").write_text("import os\nTOKEN=[REDACTED]`
- Recommendation: Move secrets to runtime env and keep only placeholders in repo.

### 9. [HIGH] Potential secret pattern: api_key_assignment
- Category: `secret_scan`
- Location: `tests/repo_audit/test_repo_auditor.py:9`
- Evidence: `(tmp_path / "secret.txt").write_text("api_key=[REDACTED]`
- Recommendation: Move secrets to runtime env and keep only placeholders in repo.

### 10. [LOW] Config risk: debug_enabled
- Category: `config_audit`
- Location: `tests/repo_audit/test_repo_auditor.py:8`
- Evidence: `(tmp_path / "config.ini").write_text("debug=true\n")`
- Recommendation: Confirm this setting is lab-only or restrict it for production.

### 11. [HIGH] Potential secret pattern: api_key_assignment
- Category: `secret_scan`
- Location: `tests/telegram/test_mission_operator.py:75`
- Evidence: `config = TelegramConfig(bot_token=[REDACTED] allowed_user_ids=["diego_claros"])`
- Recommendation: Move secrets to runtime env and keep only placeholders in repo.

### 12. [HIGH] Potential secret pattern: api_key_assignment
- Category: `secret_scan`
- Location: `tests/telegram/test_mission_operator.py:94`
- Evidence: `config = TelegramConfig(bot_token=[REDACTED] allowed_user_ids=["diego_claros"])`
- Recommendation: Move secrets to runtime env and keep only placeholders in repo.

### 13. [HIGH] Potential secret pattern: api_key_assignment
- Category: `secret_scan`
- Location: `tests/telegram/test_telegram_gateway.py:28`
- Evidence: `config = TelegramConfig(bot_token=[REDACTED] allowed_user_ids=["123"], mode="real")`
- Recommendation: Move secrets to runtime env and keep only placeholders in repo.

### 14. [HIGH] Potential secret pattern: api_key_assignment
- Category: `secret_scan`
- Location: `tests/telegram/test_telegram_gateway.py:39`
- Evidence: `config = TelegramConfig(bot_token=[REDACTED] + "secret-token", allowed_user_ids=[], mode="real")`
- Recommendation: Move secrets to runtime env and keep only placeholders in repo.

### 15. [HIGH] Potential secret pattern: api_key_assignment
- Category: `secret_scan`
- Location: `tests/telegram/test_telegram_gateway.py:48`
- Evidence: `config = TelegramConfig(bot_token=[REDACTED] + "ABC-secret", allowed_user_ids=[], mode="real")`
- Recommendation: Move secrets to runtime env and keep only placeholders in repo.

### 16. [HIGH] Potential secret pattern: api_key_assignment
- Category: `secret_scan`
- Location: `tests/telegram/test_phase_6b_3_real_gated.py:33`
- Evidence: `cfg = TelegramConfig(mode="real", bot_token=[REDACTED] allowed_user_ids=["123"])`
- Recommendation: Move secrets to runtime env and keep only placeholders in repo.

### 17. [HIGH] Potential secret pattern: api_key_assignment
- Category: `secret_scan`
- Location: `tests/telegram/test_phase_6b_3_real_gated.py:42`
- Evidence: `cfg = TelegramConfig(mode="real", bot_token=[REDACTED] + "secretTOKENvalue", allowed_user_ids=[])`
- Recommendation: Move secrets to runtime env and keep only placeholders in repo.

### 18. [HIGH] Potential secret pattern: api_key_assignment
- Category: `secret_scan`
- Location: `tests/telegram/test_phase_6b_3_real_gated.py:51`
- Evidence: `cfg = TelegramConfig(mode="mock", bot_token=[REDACTED] allowed_user_ids=[])`
- Recommendation: Move secrets to runtime env and keep only placeholders in repo.

### 19. [HIGH] Potential secret pattern: api_key_assignment
- Category: `secret_scan`
- Location: `tests/telegram/test_phase_6b_3_real_gated.py:58`
- Evidence: `token = [REDACTED] + "secretTOKENvalue"`
- Recommendation: Move secrets to runtime env and keep only placeholders in repo.

### 20. [HIGH] Potential secret pattern: api_key_assignment
- Category: `secret_scan`
- Location: `tests/telegram/test_phase_6b_3_real_gated.py:59`
- Evidence: `cfg = TelegramConfig(mode="real", bot_token=[REDACTED] allowed_user_ids=[])`
- Recommendation: Move secrets to runtime env and keep only placeholders in repo.

### 21. [HIGH] Potential secret pattern: api_key_assignment
- Category: `secret_scan`
- Location: `tests/telegram/test_phase_6b_3_real_gated.py:69`
- Evidence: `cfg = TelegramConfig(mode="real", bot_token=[REDACTED] + "secretTOKENvalue", allowed_user_ids=["123"])`
- Recommendation: Move secrets to runtime env and keep only placeholders in repo.

### 22. [HIGH] Potential secret pattern: api_key_assignment
- Category: `secret_scan`
- Location: `tests/telegram/test_phase_6b_3_real_gated.py:124`
- Evidence: `cfg = TelegramConfig(mode="mock", bot_token=[REDACTED] allowed_user_ids=[])`
- Recommendation: Move secrets to runtime env and keep only placeholders in repo.

### 23. [HIGH] Potential secret pattern: api_key_assignment
- Category: `secret_scan`
- Location: `tests/unit/test_audit_logger.py:11`
- Evidence: `log = logger.log_action({"command": "export API_KEY=[REDACTED]`
- Recommendation: Move secrets to runtime env and keep only placeholders in repo.

### 24. [HIGH] Potential secret pattern: api_key_assignment
- Category: `secret_scan`
- Location: `tests/security/test_evidence_redaction.py:13`
- Evidence: `store.append_action("test_mission", {"command": "export API_KEY=[REDACTED]`
- Recommendation: Move secrets to runtime env and keep only placeholders in repo.

### 25. [HIGH] Potential secret pattern: private_key
- Category: `secret_scan`
- Location: `tests/security/test_secret_redaction.py:9`
- Evidence: `data = {"output": "-----BEGIN RSA PRIVATE KEY-----"}`
- Recommendation: Move secrets to runtime env and keep only placeholders in repo.

### 26. [HIGH] Potential secret pattern: private_key
- Category: `secret_scan`
- Location: `tests/security/test_secret_redaction.py:11`
- Evidence: `assert "-----BEGIN RSA PRIVATE KEY-----" not in redacted.get("output", "")`
- Recommendation: Move secrets to runtime env and keep only placeholders in repo.

### 27. [HIGH] Potential secret pattern: api_key_assignment
- Category: `secret_scan`
- Location: `tests/security/test_secret_redaction.py:14`
- Evidence: `data = {"command": "export API_KEY=[REDACTED]`
- Recommendation: Move secrets to runtime env and keep only placeholders in repo.

### 28. [LOW] Config risk: bind_all_interfaces
- Category: `config_audit`
- Location: `tests/sandbox/test_network_jailer.py:9`
- Evidence: `allowed_networks=["10.0.0.0/8"],`
- Recommendation: Confirm this setting is lab-only or restrict it for production.

### 29. [HIGH] Potential secret pattern: api_key_assignment
- Category: `secret_scan`
- Location: `saga_fusion/audit_logger.py:39`
- Evidence: `(r'(?i)api[_-]?key\s*[=:]\s*([a-zA-Z0-9_-]+)', r'api_key=[REDACTED]`
- Recommendation: Move secrets to runtime env and keep only placeholders in repo.

### 30. [HIGH] Potential secret pattern: api_key_assignment
- Category: `secret_scan`
- Location: `saga_fusion/audit_logger.py:40`
- Evidence: `(r'(?i)token\s*[=:]\s*([a-zA-Z0-9_-]+)', r'token=[REDACTED]`
- Recommendation: Move secrets to runtime env and keep only placeholders in repo.

### 31. [HIGH] Potential secret pattern: api_key_assignment
- Category: `secret_scan`
- Location: `saga_fusion/audit_logger.py:42`
- Evidence: `(r'(?i)password\s*[=:]\s*(\S+)', r'password=[REDACTED]`
- Recommendation: Move secrets to runtime env and keep only placeholders in repo.

### 32. [HIGH] Potential secret pattern: api_key_assignment
- Category: `secret_scan`
- Location: `saga_fusion/llm/llm_config.py:68`
- Evidence: `api_key = [REDACTED] if config.api_key and config.api_key != "local" else config.api_key`
- Recommendation: Move secrets to runtime env and keep only placeholders in repo.

### 33. [HIGH] Potential secret pattern: api_key_assignment
- Category: `secret_scan`
- Location: `saga_fusion/llm/llm_config.py:74`
- Evidence: `f"api_key=[REDACTED] "`
- Recommendation: Move secrets to runtime env and keep only placeholders in repo.

### 34. [HIGH] Potential secret pattern: api_key_assignment
- Category: `secret_scan`
- Location: `saga_fusion/telegram/telegram_config.py:58`
- Evidence: `self.bot_token = [REDACTED] or "").strip()`
- Recommendation: Move secrets to runtime env and keep only placeholders in repo.

### 35. [HIGH] Potential secret pattern: api_key_assignment
- Category: `secret_scan`
- Location: `saga_fusion/telegram/telegram_config.py:76`
- Evidence: `f"bot_token=[REDACTED] "`
- Recommendation: Move secrets to runtime env and keep only placeholders in repo.

## Dry-Run Confirmation
- Code modified by audit: NO
- External pentest target touched: NO
- CloudOps production action executed: NO
- Patches applied automatically: NO

## Verdict
APTO PARA CONTINUAR 6C LAB: SI
