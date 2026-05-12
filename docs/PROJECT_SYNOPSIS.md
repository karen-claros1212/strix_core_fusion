# STRIX ELITE CYBER AGENT - Project Synopsis

## Purpose
STRIX Elite Cyber Agent is the single STRIX core with Saga Fusion as the owned security, sandbox, evidence, Telegram, and CloudOps layer.

## Current Root
`/mnt/Proyectos/strix_core_fusion`

## Phase Status
- Phase 0+1: baseline/documentation
- Phase 2/2.5: Saga Fusion over real STRIX
- Phase 3/3.5: tests/regression
- Phase 4: Evidence Store + Output Budget + Runtime Safety
- Phase 5: CloudOps / InfraOps Operator
- Phase 6B-2: Telegram mock mode completed
- Phase 6B-3: gated real Telegram integration completed
- Current full suite: 141 passed, 3 warnings

## Architecture
- `strix/`: STRIX core; not modified in Phase 6B-3
- `saga_fusion/`: owned Saga Fusion layer
- `saga_fusion/runtime/sandbox/`: mandatory sandbox runtime
- `saga_fusion/telegram/`: official Telegram interface
- `saga_fusion/evidence/`: evidence capture

## Telegram Phase 6B-3 Summary
- Real mode is gated by env/config and refuses startup when required settings are missing.
- Mock mode remains intact and requires no token.
- Real token is env-only via `TELEGRAM_BOT_TOKEN`.
- Allowed users are required for real mode via `TELEGRAM_ALLOWED_USER_IDS`.
- Rate limiting, replay protection, approval hashes, R4 approvals, R5 blocking, evidence logging, and output/secret redaction are active.
- Tests use mock/injected clients and do not call Telegram real APIs.

## Core Rules
- STRIX is the only core.
- Telegram is an interface, not a separate project.
- R4 requires approval.
- R5 is blocked.
- Nothing executes outside `SandboxController`.
- No real secrets in repository.


## Phase 6B-4 LLM Brain Gateway
- Added `saga_fusion/llm/` as the local brain gateway for OpenAI-compatible Qwen/TurboQuant/llama.cpp endpoints.
- LLM is disabled by default via `STRIX_LLM_ENABLED=false`.
- Endpoint/model/API key are env-driven; code has no hardcoded LLM endpoint or key.
- Natural Telegram messages may be structured by the brain only when enabled, then still pass through MissionPolicy, ApprovalWorkflow, SandboxController, and EvidenceLogger.
- Unit tests mock the LLM and never call the real endpoint.


## Phase 6B-4B Canonical ES/EN Action Normalization
- Added deterministic ES/EN mission action normalization before risk classification.
- Destructive intents such as `elimina servidor` and `borra backups` canonicalize to `delete` and become R5 blocked.
- Infrastructure-changing intents such as `crea VPS`, `cambia DNS`, `abre puerto`, and `restaura backup` canonicalize to R4 approval-required actions.
- Highest risk wins when benign/R4 and destructive terms appear together.


## Phase 6C-1 STRIX Core Repository Audit Dry-Run
- Added `saga_fusion/repo_audit/` to audit the STRIX repository as an internal lab target.
- Scope includes file inventory, Python import topology, secret-pattern scan, Docker/Compose risk scan, configuration insecurity scan, evidence JSON, and markdown report.
- Audit is dry-run only: no patches applied, no external pentest target touched, no production CloudOps executed.


## Phase 7A — CAI Pattern Source Audit
- CAI/Kai source reference audited from public `aliasrobotics/cai` tree metadata and repository docs.
- No CAI code was copied, no CAI runtime was created, and no STRIX functional logic was modified.
- Useful pattern areas identified: guardrails, tool routing, dangerous action handling, report generation, prompt hardening, task planning, memory/context, HITL, defensive workflows, and DFIR/reverse-engineering taxonomy.


## Phase 7B — CAI Pattern Implementation Plan
- Converted 7A matrix into a clean-room Saga Fusion implementation plan.
- Planned phases 7C-7J across prompt security, tool routing, dangerous action handling, HITL, reporting, task planning, defensive templates, and memory/context.
- No runtime code implemented.


## Phase 7C — Prompt Security Layer
- Added native Saga Fusion prompt security package under `saga_fusion/prompt_security/`.
- Natural Telegram text now passes through prompt security before LLM routing.
- Prompt injection, system prompt exfiltration, secret exfiltration, and policy/sandbox/evidence bypass attempts are blocked before LLM calls.


## Phase 7D — Tool Routing Layer
- Added native Saga Fusion tool routing under `saga_fusion/tool_routing/`.
- Tool routing classifies tool intents, applies route policy, and builds dry-run execution plans without executing tools.
- `TelegramMissionOperator` records tool route evidence while MissionPolicy remains authoritative.


## Phase 7E — Dangerous Action Handling
- Added `saga_fusion/policy/` with dangerous-action detector, policy, and explainer.
- MissionPolicy and ToolRouter now consult dangerous-action decisions before allowing fallback classifications.
- Critical destructive, exfiltration, bypass, and firewall-disable patterns are R5 blocked; cloud creation and limited firewall exposure require R4 approval.


## Phase 7F — HITL Approval Gates
- Added `saga_fusion/approval/` for structured R4 approval requests, store, policy, verifier, and audit.
- R4 approvals now require approval_id and exact action_hash; used/expired/hash-mismatched/unauthorized approvals fail.
- R5 actions do not create approval requests.

## Phase 7G — Structured Reporting Layer
- Added `saga_fusion/reporting/` for structured mission reports, executive summaries, technical reports, evidence summaries, Telegram-safe summaries, and report-level secret redaction.
- Reporting preserves artifact/evidence references while redacting Telegram tokens, LLM API keys, Authorization Bearer values, private keys, and sensitive key-value fields.
- Telegram report sending now prefers safe summaries plus artifact references for long reports.

## Phase 7H — Task Planner / Pattern Registry
- Added `saga_fusion/task_planning/` for deterministic clean-room pattern lookup, task plans, task-plan policy decisions, and execution intents.
- Planner produces declarative plans/intents only; `execution_allowed` remains false and no direct tool execution path exists.
- Unknown requests require policy review, R4 infrastructure changes produce approval-required intents, and R5 destructive/exfiltration requests produce blocked non-approvable intents.
- Telegram mock flow records `task_plan_intent` evidence for reporting while MissionPolicy, ToolRouter, ApprovalVerifier, and SandboxController remain authoritative.

## Phase 7I — Defensive Workflow Templates
- Added `saga_fusion/workflows/` with 8 defensive workflow templates: repository audit, secret audit, dependency audit, Docker/Compose audit, configuration audit, log review, hardening plan, and incident-response triage.
- Workflows generate `WorkflowPlan` objects only and keep `execution_allowed=False` in all current paths.
- Secret and log workflows redact secret-like values; Docker/config workflows produce evidence and recommendations only.
- TaskPlanner selects workflow plans by user intention; Reporting and Telegram mock summarize them without real remediation, CloudOps, pentest, or containment actions.

## Phase 7J — Memory / Context Patterns
- Added `saga_fusion/memory/` with memory scopes, sensitivity labels, redaction, in-memory storage, mission memory, context windowing, session summarization, policy checks, and retrieval.
- Memory redacts tokens, API keys, Authorization headers, cookies, `.env`, private keys, SSH paths, passwords, and generic secrets before storage; secret-like records are marked `SECRET_BLOCKED` and excluded from LLM context.
- BrainService/PromptBuilder include retrieved context only as non-authoritative/untrusted context; Telegram mission handling stores redacted mission memory after plan/report outcomes.
- Memory cannot become system instructions, cannot lower R4/R5, and cannot override PromptSecurity or MissionPolicy.

## Phase 8A — Hermes Source Audit + Capability Matrix
- Audited Hermes Agent as a reference source using local STRIX references plus public `NousResearch/hermes-agent` GitHub tree metadata and public docs/README references only.
- Local STRIX Hermes Agent source was not found; unrelated React Native/Hermes JS engine and vLLM parser packages in other project directories were explicitly excluded.
- Created Hermes source tree metadata snapshot, capability matrix, extraction plan, and `extensions/hermes_patterns/README.md`.
- No Hermes source code was copied, no Hermes runtime/gateway/tool/plugin integration was created, and no STRIX functional logic was modified.
- Useful clean-room pattern areas identified: toolset scoping, approval/HITL gateway regressions, cron/long-running task patterns, skill/plugin metadata, session recovery, context compression, evidence manifests, observability, and security guardrails.

<!-- PHASE_8A_BIS_SYNOPSIS -->
## Phase 8A-BIS — Hermes Source Checkout Read-Only Audit
- Cloned official `NousResearch/hermes-agent` into ignored `external_sources/hermes-agent` for read-only audit.
- Audited commit: `bfc84bdc6f85c14715e06d5fa83192ea3e7c7f79`; license observed: MIT License.
- Generated commit/doc/source-tree/capability-grep artifacts plus capability matrix, extraction plan, and gap analysis.
- Identified clean-room candidates for 8C/8D/8E: metadata, memory/context fencing, tool loop guardrails, approval timeout semantics, evidence manifests, dry-run scheduler, session recovery, and LLM error taxonomy.
- No Hermes code was copied, no Hermes dependencies installed, no Hermes runtime executed, and no STRIX core/Agent Zero/OpenCLAW/Qwen/TurboQuant/llama.cpp/WSL2/real tokens were touched.

<!-- PHASE_8B_REV_SYNOPSIS -->
## Phase 8B-REV — Hermes Pattern Design Reconciliation
- Reconciled the Phase 8A-BIS Hermes source audit into a clean-room implementation design backlog for phases 8C through 8I.
- Produced docs/reports only: no Hermes code copy, execution, runtime integration, gateway/toolset/plugin host, scheduler, or functional STRIX implementation.
- Prioritized extension governance, skill/plugin metadata, toolset scoping, dry-run scheduler, session recovery, context compression safety, evidence manifests, LLM error taxonomy, approval timeout tests, and tool loop guardrails.
- Next phases remain gated: 8C–8I each require separate approval, focused tests, full pytest, and preservation of R4/R5/SandboxController authority.

## Phase 8C — Skill / Plugin Metadata Governance
- Added `saga_fusion/skills/` for STRIX-owned declarative skill/plugin metadata.
- Skill manifests are metadata only and include permissions, allowed tools, required env names, risk level, enabled state, and entrypoint strings.
- Registry rejects duplicates/invalid manifests and supports enable/disable/list-enabled lifecycle.
- Policy blocks unknown/disabled/R5 skills, requires approval for R4, blocks direct secret requests, and rejects MissionPolicy/SandboxController bypass attempts.
- TaskPlanner can carry skill metadata references; ToolRouter enforces `allowed_tools` in skill context.
- No skill execution, plugin host, Hermes code copy, or Hermes execution was introduced.
- Full suite: 264 passed, 3 warnings.

## Phase 8D — Toolset Scoping + Tool Loop Guardrails
- Added `saga_fusion/tool_scoping/` for STRIX-owned tool scope policy, loop guardrails, toolset registry, and scoped router wrapper.
- Tool scopes can be constrained by mission, workflow, toolset, and skill metadata; unknown, denied, and out-of-scope tools are blocked.
- R4 tools remain approval-required; R5/destructive requests remain blocked even when nominally in scope.
- Tool loop guard blocks max per-mission tool-call budgets, repeated same tool+args loops, and recursive tool invocation attempts.
- `ScopedToolRouter` preserves the existing `ToolRouter` and keeps execution plans dry-run/non-executing; no Hermes code/runtime/toolset or direct execution path was introduced.
- Full suite: 278 passed, 3 warnings.

## Phase 8E — Dry-Run Scheduler / Cron Patterns
- Added `saga_fusion/scheduler/` for STRIX-owned scheduled-job metadata and cron-pattern validation.
- Scheduler records owner, timeout, enabled state, dry-run status, evidence refs, safe metadata, risk, approval/block status, and cancellation state.
- Five-field cron expressions are validated and next-run timestamps are planned only.
- `execution_allowed` is forced false, `dry_run` is mandatory, and no execute/run method, OS cron job, workspace cron scheduling, or Hermes runtime/gateway/toolset was introduced.
- R4 jobs require approval metadata; R5/destructive jobs are blocked; optional `ScopedToolRouter` integration remains non-executing.
- Full suite: 291 passed, 3 warnings.

## Phase 8F — Session Recovery + Context Compression Safety
- Added clean-room Saga Fusion session safety package under `saga_fusion/session/`.
- Session snapshots are metadata-only, checksummed, expiring, and file-serializable/in-memory safe.
- Context compression enforces budgets, excludes secret-bearing context, and marks all recovered context non-authoritative and non-executable.
- PromptBuilder can include `CompressedContext` only as untrusted user-context background; system/developer instruction injection from summaries is neutralized.
- R4/R5 risk cannot be downgraded by recovered context; MissionPolicy, PromptSecurity, and SandboxController remain authoritative.
- Validation: session `12 passed`; memory+llm+session `46 passed`; full suite `303 passed, 3 warnings`.
