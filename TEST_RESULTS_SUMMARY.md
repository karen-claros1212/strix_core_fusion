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


## Test Results (Phase 7D)
- Tool routing tests: 10 passed
- PromptSecurity + Telegram + ToolRouting tests: 64 passed
- Full suite: 195 passed, 3 warnings
- Added tests for registry metadata, classification, route policy, execution plans, unknown blocking, R4 approval, and R5 blocking.


## Test Results (Phase 7E)
- Policy tests: 7 passed
- PromptSecurity + ToolRouting + Telegram + Policy tests: 71 passed
- Full suite: 202 passed, 3 warnings
- Added tests for destructive filesystem, secret exfiltration, infra/backup destruction, firewall exposure, policy bypass, and benign status.


## Test Results (Phase 7F)
- Approval tests: 7 passed
- Policy + ToolRouting + Telegram + Approval tests: 66 passed
- Full suite: 209 passed, 3 warnings
- Added tests for unique approval IDs, stable action hashes, expiration, used/replay, hash mismatch, unauthorized user, nonexistent approval, R5 rejection, and Telegram approve/deny regressions.

## Test Results (Phase 7G)
- Reporting tests: 8 passed
- Approval + Policy + ToolRouting + Telegram + Reporting tests: 74 passed
- Full suite: 217 passed, 3 warnings
- Added tests for structured reports, executive and technical rendering, evidence JSON loading, Telegram summarization/truncation, artifact references, and report redaction.


## Test Results (Phase 7H)
- Task planning tests: 9 passed
- TaskPlanning + Approval + Policy + ToolRouting + Telegram + Reporting tests: 83 passed
- Full suite: 226 passed, 3 warnings
- Added tests for deterministic pattern registry, safe task planning, R4 approval intents, R5 blocked intents, unknown-pattern policy review, non-execution, reporting metadata, LLMRouter helper, and Telegram mock evidence regression.

## Test Results (Phase 7I)
- Workflow tests: 12 passed
- TaskPlanning + Reporting + Telegram + Workflows tests: 71 passed
- Full suite: 238 passed, 3 warnings
- Added tests for 8-template registry, unknown-workflow non-execution, all `execution_allowed=False`, workflow plan generation, R4/R5 non-execution regression, hardening/IR no real actions, secret/log redaction, Docker privileged/exposed-port fixture detection, config insecure-default detection, TaskPlanner workflow selection, Reporting summary, and Telegram mock workflow plan response.

## Test Results (Phase 7J)
- Memory tests: 12 passed
- TaskPlanning + Reporting + Telegram + Memory tests: 71 passed
- Full suite: 250 passed, 3 warnings
- Added tests for token/`.env`/private-key redaction and fingerprints, no raw secret storage, mission memory redaction, bounded context windows, `SECRET_BLOCKED` exclusion, session summaries, R4/R5 non-downgrade, untrusted/user-approved policy semantics, and retriever relevance/scope/sensitivity filtering.


## Test Results (Phase 8A)
- Full suite: 250 passed, 3 warnings
- Command: `python3 -m pytest tests -q --tb=short`
- Phase 8A is audit/documentation only: no functional logic changes, no Hermes code copy, no Hermes runtime, no Hermes integration.

<!-- PHASE_8A_BIS_TEST_RESULTS -->
## Phase 8A-BIS — Hermes Source Checkout Read-Only Audit
- Command: `python3 -m pytest tests -q --tb=short`
- Result: `250 passed, 3 warnings in 491.20s (0:08:11)`
- Log: `reports/phase_8a_bis_full_tests.log`
- Environment note: local user-level test dependencies `pytest` and `psutil` were installed because the container initially lacked them; no Hermes dependencies were installed.
- Scope touched: documentation/reports/gitignore only; no STRIX core runtime changes.

<!-- PHASE_8B_REV_TEST_RESULTS -->
## Phase 8B-REV — Hermes Pattern Design Reconciliation
- Command: `python3 -m json.tool reports/PHASE_8B_REV_HERMES_PATTERN_BACKLOG.json >/tmp/phase_8b_rev_backlog.validated.json`
- Result: JSON backlog validation passed.
- Command: `python3 -m pytest tests -q --tb=short`
- Result: `250 passed, 3 warnings in 191.21s (0:03:11)`
- Phase 8B-REV is docs/reports/status only: no functional logic changes, no Hermes code copy, no Hermes runtime, no Hermes integration.

## Test Results (Phase 8C)
- Skills suite: 14 passed
- Task planning + tool routing + skills: 33 passed
- Full suite: 264 passed, 3 warnings
- Added tests for valid manifest acceptance, duplicate rejection, disabled/unknown skill blocking, R4 approval requirement, R5 blocking, dangerous permission rejection, env-name-only handling without secret exposure, allowed_tools enforcement, metadata-only planning references, and no direct execution.

## Test Results (Phase 8D)
- Tool scoping suite: 14 passed
- Skills + tool routing + tool scoping: 38 passed
- Full suite: 278 passed, 3 warnings
- Added tests for in-scope allow, out-of-scope blocking, unknown tool blocking, R4 approval requirement, R5 blocking, skill no-widen enforcement, repeated tool-loop blocking, recursion blocking, toolset registry defaults, scoped-router no-execution behavior, and existing ToolRouter/SkillPolicy regression integrity.

## Test Results (Phase 8E)
- Scheduler suite: 13 passed
- Skills + tool routing + tool scoping + scheduler: 51 passed
- Full suite: 291 passed, 3 warnings
- Added tests for valid dry-run jobs, invalid cron rejection, mandatory `execution_allowed=False`, owner requirement, timeout bounds, cancellation/no-next-run behavior, R4 approval-required jobs, R5/destructive blocking, absence of execute/run methods, evidence metadata redaction, and scoped-router integration without execution.

## Test Results (Phase 8F)
- Session suite: `12 passed`
- Relevant subset (`tests/memory tests/llm tests/session`): `46 passed`
- Full suite: `303 passed, 3 warnings`
- Added tests for valid recovery, checksum tamper rejection, snapshot expiry rejection, secret exclusion/redaction, compression budget enforcement, non-authoritative compressed context, R4/R5 downgrade prevention, summary instruction neutralization, no execution surface, and redacted memory/context integration.

## Test Results (Phase 8G)
- Manifest suite: `13 passed`
- Relevant subset (`tests/manifests tests/reporting`): `23 passed`
- Full suite: `318 passed, 3 warnings`
- Added tests for valid manifest acceptance, invalid hash rejection, no secret-bearing raw content embedding, required redaction status for sensitive artifacts, path/reference-only artifact refs, enforced non-authoritative/non-executable flags, report-to-evidence linking, missing evidence link rejection, tamper detection, ReportRedactor reuse, Telegram-safe manifest summary, and no direct execution surface.

## Test Results (Phase 8H)
- LLM suite: `31 passed`
- Relevant subset (`tests/llm tests/prompt_security tests/session`): `55 passed`
- Full suite: `327 passed, 3 warnings`
- Added tests for auth nonretry/redaction, timeout retry within bounds, rate-limit max retry exhaustion, invalid response classification, context-too-large classification, unsafe output safe fallback, no infinite retry loops, evidence redaction, R4/R5 no-downgrade recovery, and no real LLM calls from ambient env.

## Test Results (Phase 8I)
- Approval suite: `14 passed`
- Relevant subset (`tests/approval tests/telegram tests/manifests`): `69 passed`
- Full suite: `334 passed, 3 warnings`
- Added tests for TTL boundary expiry, just-before-expiry approval, used approval replay blocking, hash mismatch blocking, unauthorized actor blocking, denied approval irreversibility, nonexistent approval blocking, R5 no-approval/non-approvable behavior, non-executing approval success, audit redaction, and regression matrix coverage.

## Test Results (Phase 8I follow-up — approval LLM isolation)
- Approval suite: `14 passed in 0.08s`
- Relevant subset (`tests/approval tests/telegram tests/manifests`): `69 passed in 0.12s`
- Full suite: `334 passed, 3 warnings in 2.34s`
- Approval regression tests now disable ambient LLM config in-process and use `/mission` command inputs for Telegram approval coverage, preventing unit tests from reaching local LLM gateways.


## Test Results (Phase 9C)
- Golden policy evaluation: `13 passed in 0.07s`.
- Targeted policy/security/approval/telegram: `84 passed, 1 existing warning in 0.13s`.
- Full first-party suite: `359 passed, 3 existing warnings in 2.36s`.
- Canonical full validation command used: `python3 -m pytest tests -q`.

## Test Results (Phase 10A)
- Cyber knowledge suite: 10 passed
- Full suite: 369 passed, 3 warnings
- Added tests for malware taxonomy classification, MITRE mapping, defensive YARA/Sigma output and rejection paths, incident playbook non-execution, and redacted non-authoritative threat reports.

## Test Results (Phase 10B)
- Defensive workflows: 10 passed
- Cyber knowledge + defensive workflows: 20 passed
- Full suite: 379 passed, 3 warnings
- Added tests for each workflow plan, safety flags, unknown registry blocking, reporter redaction, no sample execution, no attachment execution, no file deletion/encryption/decryption, no webshell generation, and no secret exposure.


## Phase 10C Test Results
- `python3 -m pytest tests/telegram -q --tb=short` — 56 passed.
- `python3 -m pytest tests/defensive_workflows tests/cyber_knowledge tests/telegram -q --tb=short` — 76 passed.
- `python3 -m pytest tests -q --tb=short` — 393 passed, 3 warnings.
