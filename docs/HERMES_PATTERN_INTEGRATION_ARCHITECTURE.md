# Hermes Pattern Integration Architecture — STRIX Clean-Room Plan

## Boundary
Hermes Agent is an external reference only. The audited checkout lives at `external_sources/hermes-agent` and is ignored by git. STRIX must not import, execute, vendor, install, or copy from it.

## Phase 8B-REV reconciliation
Phase 8B-REV reconciles the Phase 8A-BIS source audit into a forward design backlog. It is documentation/reporting only: no runtime code, no gateway, no scheduler, no provider/plugin host, no functional STRIX behavior changes.

## Authoritative STRIX controls
- `MissionPolicy` and `DangerousActionPolicy` classify and block unsafe intent.
- `ToolRouter` and `ToolRoutePolicy` create declarative execution plans only.
- `ApprovalVerifier` gates R4 with approval IDs and exact action hashes.
- R5 remains blocked and non-approvable.
- `SandboxController` remains the only execution boundary.
- `EvidenceLogger`, `Reporting`, and secret redactors remain mandatory for user-visible and stored outputs.
- Memory/context is non-authoritative and cannot override policy.

## Clean-room adaptation lanes
1. **Phase 8C — Skill/Plugin Metadata Governance**
   - STRIX-owned extension/workflow metadata schema.
   - Provenance, owner, source/license, risk tier, allowed capabilities, disabled-by-default lifecycle.
   - No runtime plugin host and no Hermes skill ingestion.
2. **Phase 8D — Toolset Scoping + Tool Loop Guardrails**
   - Tool scope vocabulary mapped to STRIX risk model.
   - Idempotent/mutating taxonomy, repeated-failure/no-progress circuit breakers.
   - No parallel Hermes toolset or gateway.
3. **Phase 8E — Dry-Run Scheduler/Cron Patterns**
   - Non-executing schedule specifications only.
   - Timezone, owner, scope, budget, stale approval, delivery/evidence manifest requirements.
   - No OS cron wiring or unattended real actions.
4. **Phase 8F — Session Recovery + Context Compression Safety**
   - STRIX-owned restart/pending-drain/session recovery state machine.
   - Non-authoritative compaction summaries, protected policy/redaction/approval invariants.
   - No Hermes gateway adoption.
5. **Phase 8G — Evidence/Reporting Manifests**
   - Standard artifact manifest schema with phase, generator, source commit, redaction status, validation commands/results, and delivery references.
   - No secret metadata or external source content.
6. **Phase 8H — LLM Error Taxonomy + Recovery**
   - Transient/auth/rate-limit/context/safety/provider/unknown classification.
   - Reporting-first recovery and bounded retry evidence.
   - No credential rotation, hidden fallback, or real LLM calls in tests.
7. **Phase 8I — Approval Timeout + Regression Depth**
   - Timeout-to-deny, stale approval denial, wrong-user/channel denial, exact hash checks.
   - Expanded risk-based regression matrix.
   - No allow-always behavior.

## Prohibited integration paths
- No Hermes gateway/platform registry in STRIX runtime.
- No Hermes plugin host, provider plugins, skills, or self-improvement loops.
- No Hermes installer/dependency reuse.
- No automatic credential rotation or provider fallback.
- No real-token or `.env` access.
- No Agent Zero, OpenCLAW, Qwen, TurboQuant, llama.cpp, WSL2, Telegram real, CloudOps real, or external pentest changes.

## Evidence requirements for future phases
Every future Hermes-inspired implementation must include: source-pattern citation by path, clean-room design note, risk classification, tests, redaction behavior, full-suite result, explicit `what_not_to_do`, and confirmation that STRIX policy/approval/sandbox controls remain authoritative.

## Current 8B-REV deliverables
- `reports/PHASE_8B_REV_HERMES_PATTERN_DESIGN_RECONCILIATION.md`
- `reports/PHASE_8B_REV_HERMES_PATTERN_BACKLOG.json`
- Updated `extensions/hermes_patterns/README.md`
- Updated project status files

## Phase 8C completion — Skill/Plugin Metadata Governance
Phase 8C implements a STRIX-owned metadata governance layer under `saga_fusion/skills/`. It provides manifest validation, registry lifecycle, and policy decisions only. It does not add a runtime plugin host, Hermes skill ingestion, Hermes gateway/toolset, or skill execution.

Skill metadata is subordinate to STRIX controls: unknown and disabled skills are blocked, R4 skills require approval, R5 skills are blocked, direct secret requests are rejected, and bypass attempts against MissionPolicy or SandboxController are rejected. Task planning may reference skill metadata, and ToolRouter enforces `allowed_tools` when skill context is provided.

## Phase 8D completion — Toolset Scoping + Tool Loop Guardrails
Phase 8D implements a STRIX-owned tool scoping and loop-guard layer under `saga_fusion/tool_scoping/`. It is clean-room and does not introduce a Hermes gateway, Hermes toolset runtime, or direct execution path.

`ToolScopePolicy` gates requests by mission, workflow, toolset, and skill `allowed_tools`; unknown, denied, and out-of-scope tools are blocked. R4 tools remain approval-required and R5/destructive requests remain blocked. Skills cannot widen their own declared tool scope.

`ToolLoopGuard` blocks per-mission over-budget calls, repeated same tool+args loops, and recursive tool calls with evidence metadata. `ScopedToolRouter` wraps the existing `ToolRouter` by applying scope first, loop guard second, and the existing route policy last; all generated execution plans remain dry-run/non-executing and `SandboxController` remains the only execution boundary.

## Phase 8E completion — Dry-Run Scheduler / Cron Patterns
Phase 8E implements a STRIX-owned scheduler metadata layer under `saga_fusion/scheduler/`. It validates five-field cron expressions, stores owner/timeout/enabled/dry-run/evidence metadata, supports cancellation state, and computes next-run plans only.

The scheduler is intentionally non-executing: `ScheduledJob.execution_allowed` cannot be set to true, `dry_run` cannot be disabled, `SchedulePlanner` has no execute/run method, no OS cron integration exists, and no workspace cron tools are used. R4 scheduled jobs become approval-required metadata, R5/destructive scheduled jobs are blocked, and optional `ScopedToolRouter` checks remain metadata-only. `SandboxController` remains the only possible execution boundary for any future execution phase.

## Phase 8F completion — Session Recovery + Context Compression Safety
Phase 8F implements a STRIX-owned session recovery safety layer under `saga_fusion/session/`. It is metadata/state-only and introduces no Hermes gateway, Hermes runtime, external scheduler, or execution path.

Snapshots retain only safe state metadata and inert compressed context. Raw context is not persisted in snapshots. Secret-bearing context is excluded, secret-bearing intent is replaced with a redacted exclusion marker, checksums protect snapshot integrity, and expiry prevents stale recovery.

Recovered context is explicitly non-authoritative (`non_authoritative=True`, `execution_allowed=False`) and is rendered only as untrusted user-context background for LLM prompt construction. It cannot act as a system/developer instruction, cannot override PromptSecurity/MissionPolicy/SandboxController, and cannot downgrade R4/R5 intent. Tampered, expired, authoritative, or executable snapshots are rejected.

## Phase 8G completion — Evidence / Reporting Manifests
Phase 8G implements a STRIX-owned evidence/reporting manifest layer under `saga_fusion/manifests/`. It is clean-room and introduces no Hermes runtime, gateway, toolset, or direct execution path.

Manifests store artifact references, hashes, sizes, provenance, redaction/secret-scan status, classification/risk, mission/session IDs, metadata, and safe linkage between report artifacts and evidence artifacts. They do not embed raw artifact bodies. Existing `ReportRedactor` is reused through `ManifestRedactor`, and Telegram/reporting integration exposes only safe manifest summaries or references.

`ManifestValidator` enforces SHA-256 format, existing-file tamper detection, redaction status for sensitive artifacts, no raw-body metadata keys, `non_authoritative=True`, and `execution_allowed=False`. The manifest package has no execute/run/dispatch/send/call surface; it is traceability/reporting metadata only. `SandboxController`, MissionPolicy, PromptSecurity, ApprovalVerifier, EvidenceLogger, and Reporting remain authoritative.
