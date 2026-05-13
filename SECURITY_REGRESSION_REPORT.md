# SECURITY REGRESSION REPORT

## Phase 6B-3 Telegram Real Gated Security Status
Date: 2026-05-07

## Security Controls

### Token Handling
- `TELEGRAM_BOT_TOKEN` is loaded from environment/config only.
- Real mode refuses startup without token.
- Token is redacted from `TelegramConfig.__repr__`, gateway logs, evidence, and message outputs.
- `.env.example` documents variables without real values.

### Allowlist
- `TELEGRAM_ALLOWED_USER_IDS` is required for real mode.
- Empty allowlist fails closed in real mode.
- Unauthorized users receive `DENIED`.

### Rate Limiting
- Gateway/operator use per-user rate limiting.
- `TELEGRAM_RATE_LIMIT_PER_MINUTE` is supported.

### Replay Protection and Approvals
- ApprovalWorkflow creates unique approval IDs.
- ApprovalWorkflow hashes the action payload.
- Approval fails on replayed action hash.
- Approval fails on action hash mismatch.
- R4 requires approval.
- R5 is blocked.

### Sandbox and Evidence
- Mission dispatch goes through `SandboxDispatcher` and `SandboxController`.
- R5 never dispatches.
- EvidenceLogger records incoming message, authorization, policy, approval, mission, and sandbox events with redaction.

### Secret Scan
- No real secrets found.
- Scan output contains expected variable names, code redaction patterns, and historical/test fixtures only.

### Legacy Telegram Scan
- No active `saga_fusion/telegram_mission_operator/` runtime directory.
- No active imports to the legacy path found in `saga_fusion/telegram`.
- Historical reports still mention the removed legacy path for audit traceability.

## Verdict
Security regression status: PASS for Phase 6B-3 gated real Telegram preflight.


## Security Regression Report (Phase 6B-4)
- LLM enabled flag defaults to false.
- LLM endpoint/model/API key are env-only.
- API key is redacted in repr.
- Unit tests do not call real LLM endpoint.
- LLM failures fall back safely and do not break TelegramGateway.
- BrainService does not execute tools and cannot bypass MissionPolicy, ApprovalWorkflow, or SandboxController.
- Real mission execution remains disabled/not performed.


## Security Regression Report (Phase 6B-4B)
- Spanish/English destructive actions normalize to R5 and are blocked.
- Spanish/English infrastructure-changing actions normalize to R4 and require approval.
- Mixed intent uses highest-risk-wins semantics.
- Smoke confirmed no real action execution for R4/R5 probes.
- Secret literal scan found 0 runtime token/API-key leaks in reports/source/tests.


## Security Regression Report (Phase 6C-1)
- Repo audit runs in dry-run mode and does not apply patches.
- Secret findings are redacted before evidence/report output.
- Runtime secret literal scan on 6C-1 report/evidence found 0 token/API-key leaks.
- Audit touched no external pentest targets and executed no production CloudOps action.


## Security Regression Report (Phase 6C-2)
- Triage found 0 confirmed critical/high runtime security issues after deduplication.
- Main risk is alert fatigue / documentation drift from scanner false positives around placeholders, test fixtures, and redaction code.
- No secrets were exposed by triage outputs.
- No patches or external actions were executed.


## Security Regression Report (Phase 6C-3)
- Only auto-fix-safe triage findings were patched.
- `.env.example` placeholders remain accepted only when values are blank or explicit placeholders; real-looking tokens still remain scannable.
- `tests/` config fixtures no longer inflate runtime config-risk findings.
- Manual-review findings were not modified.
- No real external action, Telegram real execution, CloudOps operation, or production mutation was performed.


## Security Regression Report (Phase 6C-4)
- Manual review found no confirmed leaked runtime secret in the three remaining findings.
- One runtime redaction-code scanner self-hit requires targeted scanner classification in 6C-5.
- Historical report findings are documentation-only and should preserve audit traceability.
- Synthetic test secret fixtures are accepted risk for redaction regression coverage.
- No Telegram real, CloudOps, pentest external, token, `.env`, architecture, or STRIX core change was performed.


## Security Regression Report (Phase 6C-5)
- Redaction code self-references are no longer reported as literal secret leaks.
- Real secret simulations in runtime code still trigger HIGH `secret_scan` findings.
- Security files are not globally excluded.
- Historical reports and synthetic fixtures were preserved.
- Accepted-risk fixture source was not modified.
- No Telegram real, CloudOps real, pentest external, token, `.env`, architecture, or STRIX core protected file change was performed.


## Security Regression Report (Phase 6C-6)
- Final dry-run re-audit found no confirmed real secret literal leak.
- No P0/P1 residual issue confirmed.
- No scanner regression identified after redaction self-reference classification.
- No active `telegram_mission_operator` runtime/import exists in `saga_fusion` or `tests`; historical report mentions remain audit traceability only.
- No Telegram real, CloudOps real, external pentest, token, `.env`, architecture, or STRIX protected core change was performed.


## Security Regression Report (Phase 7A)
- No CAI source code was copied into STRIX.
- No CAI runtime, external offensive workflow, Telegram real execution, CloudOps real action, token, `.env`, architecture, or protected core change was performed.
- CAI offensive/recon/exploit concepts are documented as patterns only and remain gated for future authorized lab phases.


## Security Regression Report (Phase 7B)
- No CAI code copied and no CAI runtime created.
- No STRIX core, Agent Zero, OpenCLAW, Hermes, Qwen/TurboQuant/llama.cpp/WSL2, token, `.env`, Telegram real, CloudOps real, or external pentest action performed.
- 7C must start with prompt security only, before tool routing or offensive/recon pattern work.


## Security Regression Report (Phase 7C)
- Prompt-injection and prompt-bypass attempts are blocked before LLM calls in natural Telegram flow.
- PromptSecurity reinforces MissionPolicy and does not replace R0-R5 classification.
- R4 VPS regression remains approval_required; R5 destructive regression remains blocked.
- No CAI code copied, no CAI runtime, no Telegram real, no CloudOps real, no external pentest, no token/`.env` change, and no STRIX core change.


## Security Regression Report (Phase 7D)
- ToolRouter does not execute tools and exposes no direct shell path.
- Unknown tools and R5 requests are blocked; R4 requires approval.
- Sandbox-required tools are marked for sandbox route/dry-run.
- PromptSecurity, Telegram mock mode, and R4/R5 regressions remain green.
- No CAI code copy, CAI runtime, Telegram real, CloudOps real, external pentest, token/`.env`, or STRIX core change was performed.


## Security Regression Report (Phase 7E)
- DangerousActionPolicy blocks critical destructive, exfiltration, bypass, backup deletion, and firewall-disable intents as R5.
- Cloud creation and limited firewall exposure require R4 approval.
- MissionPolicy remains authoritative and is reinforced before fallback classification.
- ToolRouter respects DangerousActionDecision and still does not execute tools.
- No CAI code copy, CAI runtime, Telegram real, CloudOps real, external pentest, token/`.env`, or STRIX core change was performed.


## Security Regression Report (Phase 7F)
- Generic approval without approval_id is rejected.
- R4 approvals require exact action_hash and authorized user.
- Expired, used, hash-mismatched, nonexistent, unauthorized, and R5 approvals fail.
- R5 missions remain blocked without approval creation.
- No R4 real action executed in tests; no CAI code/runtime, Telegram real, CloudOps real, external pentest, token/`.env`, or STRIX core change.

## Security Regression Report (Phase 7G)
- ReportRedactor redacts Telegram bot tokens, STRIX LLM API keys, Authorization Bearer values, private keys, sensitive key-value fields, `.env`, and SSH paths while preserving fingerprints.
- Reporting adds safe summaries and artifact references instead of exposing long/raw evidence in Telegram responses.
- R4/R5, ApprovalVerifier, ToolRouter, PromptSecurity, DangerousActionPolicy, and SandboxController semantics are not weakened.
- No CAI code/runtime, Telegram real, CloudOps real, external pentest, token/`.env`, or STRIX core change was performed.


## Security Regression Report (Phase 7H)
- TaskPlanner and ExecutionIntentBuilder produce declarative plans/intents only; execution_allowed remains false in current paths.
- R4 plans produce approval-required intent metadata only; R5 plans are blocked and non-approvable.
- Unknown patterns require policy review and do not silently allow execution.
- MissionPolicy, DangerousActionPolicy, ToolRouter, ApprovalVerifier, SandboxController, PromptSecurity, and Reporting remain authoritative.
- No CAI code/runtime, Telegram real, CloudOps real, external pentest, token/`.env`, STRIX core, Agent Zero, OpenCLAW, Hermes, Qwen/TurboQuant/llama.cpp/WSL2 change was performed.

## Security Regression Report (Phase 7I)
- Defensive workflows are declarative templates only and generate `WorkflowPlan`; no workflow executes tools, remediation, containment, CloudOps, Telegram real calls, or external pentest actions.
- All current workflow templates, steps, plans, and results set `execution_allowed=False`.
- Secret audit and log review redact secret-like values and never include full secret values in evidence/report structures.
- Docker/config workflows detect risky indicators and insecure defaults but emit recommendations only.
- Hardening and incident-response workflows explicitly create implementation/containment plans only; real containment and auto-remediation remain disabled.
- R4/R5 regression gates remain intact through TaskPlanner, MissionPolicy, ToolRouter, ApprovalVerifier, SandboxController, EvidenceLogger, and Reporting.

## Security Regression Report (Phase 7J)
- Memory is non-authoritative context only and is never promoted to system instruction authority.
- PromptSecurity remains before LLM routing; MissionPolicy remains authority for risk and execution gates.
- MemoryPolicy prevents memory from downgrading R4/R5 and excludes `SECRET_BLOCKED` records from normal retrieval/context.
- MemoryRedactor blocks raw storage of Telegram bot tokens, STRIX LLM API keys, Authorization headers, API keys, cookies, `.env`, private keys, SSH paths, passwords, and generic tokens; only redacted placeholders and safe fingerprints may persist.
- No CAI/Hermes code/runtime, Telegram real, CloudOps real, external pentest, token/`.env`, STRIX core, Agent Zero, OpenCLAW, Hermes, Qwen/TurboQuant/llama.cpp/WSL2 change was performed.


## Security Regression Report (Phase 8A)
- Local STRIX Hermes Agent source was not found; only public Hermes Agent tree metadata/docs were referenced.
- No Hermes source code was copied, no Hermes runtime/gateway/tools/plugins were created, and no Hermes integration was performed.
- No STRIX core, Agent Zero, OpenCLAW, Hermes installed, Qwen/TurboQuant/llama.cpp/WSL2, Telegram real, CloudOps real, external pentest, token, or `.env` change was performed.
- Capability extraction is documentation-only and keeps PromptSecurity, MissionPolicy, DangerousActionPolicy, ToolRouter, ApprovalVerifier, SandboxController, EvidenceLogger, Reporting, OutputBudget, SecretRedactor, and MemoryPolicy authoritative.

<!-- PHASE_8A_BIS_SECURITY -->
## Phase 8A-BIS — Hermes Source Checkout Safety Regression
- External source cloned to ignored path: `external_sources/hermes-agent`.
- No Hermes code copied into Saga Fusion.
- No Hermes execution or dependency installation occurred.
- No real token/`.env` access occurred; only `.env.example` appeared in source-tree metadata.
- STRIX core, Agent Zero, OpenCLAW, installed Hermes, Qwen/TurboQuant/llama.cpp/WSL2 were not touched.
- Security posture: documentation-only audit with clean-room extraction plan; future candidates require separate implementation approval and tests.

<!-- PHASE_8B_REV_SECURITY -->
## Phase 8B-REV — Hermes Pattern Design Safety Regression
- Reconciled Hermes patterns as clean-room design only.
- No Hermes code was copied into Saga Fusion; no Hermes execution, dependency install, runtime, gateway, toolset, plugin host, scheduler, or terminal backend was created.
- `external_sources/hermes-agent` remains ignored and must not be staged.
- STRIX core, Agent Zero, OpenCLAW, Qwen/TurboQuant/llama.cpp/WSL2, real Telegram, real CloudOps, external pentest, tokens, and `.env` were not touched.
- R4 approval, R5 blocking, `SandboxController`, EvidenceLogger/Reporting, redaction, and non-authoritative memory remain the governing controls for future phases.

## Security Regression Report (Phase 8C)
- Unknown skills are blocked.
- Disabled skills are blocked.
- R4 skill metadata requires approval.
- R5 skill metadata is blocked and non-executing.
- Direct secret requests in skill metadata are blocked; required_env stores names only and does not read/expose values.
- MissionPolicy/SandboxController bypass attempts in skill metadata are blocked.
- ToolRouter enforces `allowed_tools` when skill context is provided.
- No skill execution path, plugin host, Hermes runtime/gateway/toolset, Hermes code copy, or Hermes execution was introduced.

## Security Regression Report (Phase 8D)
- ToolScopePolicy blocks unknown tools and tools outside mission/workflow/toolset/skill scope.
- R4 tools remain approval-required and R5/destructive requests remain blocked even when listed in a permitted planning toolset.
- Skills cannot widen their own declared `allowed_tools` scope.
- ToolLoopGuard blocks repeated same tool+args calls, per-mission call-budget excess, and recursive tool invocation attempts with evidence metadata.
- ScopedToolRouter delegates only to existing ToolRouter policy after scope/loop gates and forces dry-run/non-executing execution plans.
- No Hermes code copy/execution/runtime/gateway/toolset, no direct execution, no real Telegram, no CloudOps real action, no external pentest, no tokens/`.env`, and no STRIX core/Agent Zero/OpenCLAW/Qwen/TurboQuant/llama.cpp/WSL2 changes were introduced.

## Security Regression Report (Phase 8E)
- Scheduler objects are declarative metadata only; they do not create OS cron jobs, call workspace cron tools, or execute scheduled work.
- `execution_allowed=True` and `dry_run=False` are rejected at job construction.
- Invalid cron expressions, missing owners, and out-of-bounds timeouts are rejected or blocked.
- R4 scheduled jobs require approval metadata; R5/destructive scheduled jobs are blocked and non-approvable.
- Cancellation disables jobs and prevents next-run planning.
- Evidence refs/arguments/metadata redact token/password/API-key/Authorization-like values.
- Optional `ScopedToolRouter` integration records route/scope policy decisions only and still performs no execution.
- No Hermes code copy/execution/runtime/gateway/toolset, no direct execution, no real Telegram, no CloudOps real action, no external pentest, no tokens/`.env`, and no STRIX core/Agent Zero/OpenCLAW/Qwen/TurboQuant/llama.cpp/WSL2 changes were introduced.

## Security Regression Report (Phase 8F)
- Session snapshots are metadata-only and do not persist raw context.
- Recovered context is always non-authoritative and non-executable.
- Tampered snapshots are rejected by checksum validation.
- Expired snapshots are rejected.
- Secret-bearing context is excluded and secret-bearing intent is replaced with a safe marker.
- Summary text cannot become system/developer instructions; role-like recovered text is neutralized and remains user-context-only.
- R4/R5 risk cannot be downgraded by recovered context.
- Session recovery exposes no direct execution method and does not bypass MissionPolicy, PromptSecurity, or SandboxController.
- Full regression remained green: `303 passed, 3 warnings`.

## Security Regression Report (Phase 8G)
- Manifest artifacts are references only; raw evidence/report bodies are not stored in manifests or Telegram summaries.
- SHA-256 is required and existing local paths are re-hashed to detect tampering.
- Sensitive or secret-scan-positive artifacts require explicit redaction status (`redacted`, `reference_only`, or `blocked`).
- Existing `ReportRedactor` is reused for manifest metadata/provenance and Telegram manifest summaries.
- `non_authoritative=True` and `execution_allowed=False` are enforced for artifact refs and manifests.
- Manifest package exposes no direct execution surface; no execute/run/dispatch/send/call method exists.
- No Hermes code/runtime/gateway/toolset, real Telegram, CloudOps, external pentest, token, or `.env` change was performed.

## Phase 8G follow-up — No Artifact Content Scanning
- Patched `ManifestBuilder` so local path refs never call `Path.read_text()` or decode artifact content for secret detection.
- Local path refs now default to `SecretScanStatus.NOT_SCANNED`; callers may explicitly provide `secret_scan_status` and `redaction_status` metadata.
- SHA-256/file-size hashing remains allowed and tamper detection is preserved.
- Added tests that monkeypatch `Path.read_text` to fail, proving manifest ref building does not inspect raw artifact text.

## Security Regression Report (Phase 8H)
- LLM recovery is taxonomy/reporting-first and does not execute tools or switch providers.
- Retry limits are explicit and bounded; backoff is metadata only and no sleep loop or infinite retry path exists.
- Auth, invalid response, unsafe output, context-too-large, model-unavailable, and unknown errors are nonretryable safe-fallback conditions.
- Error evidence redacts Bearer tokens, OpenAI-style keys, API keys, token/secret fields, and authorization assignments.
- Unsafe LLM output attempting tool execution, approval bypass, PromptSecurity bypass, MissionPolicy bypass, or SandboxController bypass falls back to deterministic non-executing routing.
- Recovery fallback does not downgrade R4/R5 intent; existing action normalization and MissionPolicy remain authoritative.
- Unit tests cannot call a live LLM gateway through ambient shell env because test conftest disables env-driven LLM enablement; enabled LLM paths are stubbed.
- Full regression remained green: `327 passed, 3 warnings`.

## Security Regression Report (Phase 8I)
- Approval expiry is enforced at and after the TTL boundary; just-before-expiry approvals are still valid only if all other gates pass.
- Used approvals cannot be replayed and produce `approval_replay_blocked` with `execution_allowed=False` evidence.
- Action-hash mismatches are terminal and block later approval attempts.
- Unauthorized actors are blocked without executing or mutating approval success state.
- Denied and expired approvals are irreversible/non-executing.
- Missing approval IDs and R5 approval attempts are blocked; R5 missions create no approval.
- Telegram approval success still returns `executed=False`; no action is executed by approval success.
- Audit summaries redact token/API-key/password-like values and remain metadata-only.
- Full regression remained green: `334 passed, 3 warnings`.

## Security Regression Follow-up (Phase 8I LLM Isolation)
- Approval regression tests explicitly disable ambient `STRIX_LLM_ENABLED` for the test process.
- Telegram approval regression coverage uses `/mission` command inputs, avoiding natural-language LLM routing in approval unit tests.
- Production behavior is unchanged; no real LLM, real Telegram, CloudOps, external pentest, token, or `.env` change was introduced.
- Approval suite runtime improved to `14 passed in 0.08s` while preserving full-suite status: `334 passed, 3 warnings`.


## Security Regression Report (Phase 9C)
- Policy evaluation optimization preserved MissionPolicy and PromptSecurity authority.
- R4 approval-required and R5 blocked/non-approvable semantics remained unchanged.
- Approval hash, expiry, actor authorization, denied/expired terminal states, and replay blocking remained unchanged.
- Tool scope, unknown-tool blocking, redaction, manifest non-authoritative/non-executable metadata, and SandboxController boundaries remained unchanged.
- No real Telegram, real LLM, CloudOps, external pentest, Hermes code copy/execution, direct execution, token/`.env`, Agent Zero, OpenCLAW, Qwen, TurboQuant, or llama.cpp changes were introduced.
- Full regression remained green: `359 passed, 3 existing warnings`.

## Security Regression Report (Phase 10A)
- Cyber knowledge layer is defensive classification/detection/reporting only.
- No malware samples were downloaded or executed.
- No functional malware payloads, persistence, exfiltration, AV/EDR bypass, or exploit code were created.
- YARA/Sigma builders reject offensive, payload, bypass, exfiltration, and execution requests.
- Threat reports redact secret-like values, are non-authoritative, and set `execution_allowed=False`.
- Real Telegram, real LLM/Qwen/TurboQuant/llama.cpp, external pentest, Agent Zero/OpenCLAW/Hermes, tokens, and `.env` remained untouched.

## Security Regression Report (Phase 10B)
- Advanced defensive workflows generate plans, evidence, reports, detections, and recommendations only.
- Every workflow keeps `execution_allowed=False`, `evidence_required=True`, and `report_required=True`.
- Malware triage does not download or execute samples; phishing does not execute attachments; ransomware does not delete, encrypt, or decrypt files; webshell investigation does not generate or invoke webshells; credential-theft workflow does not display secrets or exfiltrate data.
- ToolRouter remains non-executing and TaskPlanner integration is metadata/report-only.
- No real Telegram, CloudOps, external pentest, offensive payload, bypass, persistence, tokens, `.env`, Qwen/TurboQuant/llama.cpp, Agent Zero, OpenCLAW, or Hermes changes.


## Phase 10C Security Regression
- R4/R5 regression remains intact: R4 requires approval; R5 is blocked.
- Defensive Telegram lab routing returns non-authoritative report/evidence plans only.
- No real Telegram calls, real tool execution, malware execution, attachment execution/processing, offensive payloads, webshell generation, external pentest, CloudOps, token/.env changes, Qwen/TurboQuant/llama.cpp changes, or Agent Zero/OpenCLAW/Hermes changes were introduced.
- Response redaction blocks raw tokens/password-like values.

## Security Regression Report (Phase 10D-1)
- Phase 10D-1 added design documentation and golden characterization tests only; no report-pack runtime generator or execution path was introduced.
- Golden tests assert defensive workflow and Telegram lab-mode pack inputs preserve `execution_allowed=False`, `executed=False`, `evidence_required=True`, `report_required=True`, and `non_authoritative=True`.
- Future report packs must use evidence/report refs, hashes, and redacted metadata only; raw artifact bodies, attachment contents, sample bytes, credentials, tokens, and secrets remain blocked.
- No real Telegram, malware execution, payload/webshell generation, attachment execution/processing, destructive command, external network execution, config change, `.env` change, token exposure, or secret printing was performed.
- R4/R5, PromptSecurity, MissionPolicy, SandboxController, approval flow, manifest validation, and redaction remain unchanged.

## Security Regression Report (Phase 10D-2)
- `DefensiveReportPack` is a reference-only aggregation layer; it does not execute workflows, tools, Telegram, LLMs, attachments, samples, payloads, webshells, destructive commands, or network calls.
- Safety flags are enforced: `execution_allowed=False`, `executed=False`, `non_authoritative=True`, `evidence_required=True`, and `report_required=True`.
- Evidence/report artifacts are represented by refs, SHA-256 hashes, sizes, redaction status, secret-scan status, and manifest summaries only; raw body/content keys are blocked from tests and not emitted.
- Existing `ReportRedactor` and manifest redaction/validation primitives are reused; dummy token/password/Bearer values are redacted in pack outputs.
- R4/R5, PromptSecurity, MissionPolicy, SandboxController, approval flow, and manifest validation were not weakened.
- Full regression remained green: 417 passed, 3 existing warnings.
