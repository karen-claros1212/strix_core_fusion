# Phase 8A-BIS — Hermes Extraction Plan

Clean-room constraint: extract ideas only. Do not copy Hermes code, install Hermes dependencies, execute Hermes, create a Hermes gateway/runtime, or alter STRIX core.

## ADAPT_PATTERN
- Skill metadata schema: adapt the idea of `SKILL.md` metadata, reload lifecycle, allowlisted roots, and index caches into STRIX defensive workflow metadata.
- Memory context fencing: adapt provider boundary checks, single active external provider concept, and streaming scrubber tests into Saga memory protections.
- Context compression templates: adapt structured handoff summaries, active-task separation, protected head/tail, redaction, and compaction-boundary tests.
- Tool loop guardrails: adapt idempotent vs mutating tool taxonomy and no-progress/repeated-failure counters into `saga_fusion/tool_routing`.
- Approval timeout semantics: adapt timeout-to-deny and channel-specific approval audit outcomes, without allow-always defaults.
- Evidence/report manifests: adapt explicit artifact manifests with source commit, phase, redaction status, and test provenance.
- Regression taxonomy: adapt test categories for gateway session routing, restart drain, cron dry-runs, approval denial, context compaction, memory injection, and plugin governance.

## REIMPLEMENT_CLEAN
- Extension manifest governance for future STRIX extensions: disabled by default, signed/allowlisted, risk-tiered, no runtime plugin imports in current phase.
- Scheduled audit planner: start with non-executing schedule specifications and dry-run evidence only; later phases may wire to `SandboxController` after approval.
- Session recovery state machine: implement STRIX-owned Telegram session IDs, pending action drainage, restart markers, and redacted route evidence.
- LLM error taxonomy: classify LLM/provider failures for reporting and safe retry budgets; no credential rotation or unapproved provider fallback.

## DOCUMENT_ONLY
- Hermes multi-platform gateway registry and broad adapter ecosystem.
- Dashboard plugin manifests and cockpit UI concepts.
- ACP protocol bridging details beyond approval/tool-kind vocabulary.
- Curator/dogfood self-improvement reports as human backlog inspiration only.

## DISCARD
- Any Hermes runtime, gateway, terminal backend, shell hook, installer, bundled dependencies, or environment bootstrap.
- Broad provider plugin code, token/OAuth flows, Qwen OAuth plugin, WSL2/install mechanics, and Hermes-specific CLI commands.
- Allow-always approval behavior for STRIX R4/R5 decisions.
- Any autonomous self-modification or direct skill ingestion into active prompts.

## FUTURE_RESEARCH
- Phase 8C: defensive metadata/schema, memory fencing, context compression, tool loop guardrails, approval timeout regressions, evidence manifests.
- Phase 8D: dry-run scheduled audit planner, session recovery, LLM error taxonomy, restart/pending-drain evidence.
- Phase 8E: optional research on platform registry boundaries and dashboard manifests; no implementation unless separately approved.
