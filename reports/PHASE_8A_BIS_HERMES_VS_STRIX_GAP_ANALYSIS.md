# Phase 8A-BIS — Hermes vs STRIX Gap Analysis

## Hermes is stronger in
- Breadth of extension surface: skills, optional skills, plugin manifests, provider plugins, memory plugins, platform plugins, dashboard manifests.
- Gateway/session maturity: persistent multi-platform sessions, task-local contextvars, restart/pending-drain behavior, redacted session IDs, extensive gateway regressions.
- Scheduler coverage: cron scheduler, job context, next-run calculations, workdir/file-permission tests, and delivery integration.
- Context compression: token-aware compression, tool-output pruning, structured continuity summaries, image-token budgeting, and fallback tests.
- Recovery taxonomy: centralized API error classification and retry/failover hints.
- Regression depth: large test suite across gateway, cron, skills, plugins, approvals, memory, context, and adapters.

## STRIX is stronger in
- Security boundaries: MissionPolicy, DangerousActionPolicy, ToolRouter, ApprovalVerifier, SandboxController, EvidenceLogger, and SecretRedactor are explicit and authoritative.
- R4/R5 safety model: destructive/exfiltration/bypass actions are blocked or approval-gated before execution.
- Clean-room governance: STRIX refuses code copying and runtime integration from external agents unless specifically approved.
- Telegram safety: mock-first tests, env-only tokens, allowlist requirements, rate limiting, replay protection, approval hashes, and redacted reports.
- Audit discipline: phase reports, risk register, security regression report, and full-suite validation are maintained after each change.

## Do not copy
- Hermes source code, installer scripts, dependencies, runtime, gateway, terminal backends, plugin implementations, provider plugins, OAuth/token flows, shell hooks, or self-improvement loops.
- Hermes skills as active STRIX skills.
- Hermes cron execution path or multi-platform gateway.
- Any code touching Qwen/TurboQuant/llama.cpp/WSL2, Agent Zero, OpenCLAW, installed Hermes, real tokens, or `.env` secrets.

## Reimplementation candidates
- 8C: STRIX extension metadata schema, safe skill/workflow manifest, context compression template, memory streaming scrubber, tool loop guardrail counters, approval timeout-to-deny tests, evidence manifest schema.
- 8D: dry-run scheduled audit planner, Telegram session recovery state machine, restart/pending-drain audit records, LLM error taxonomy with bounded retry reporting.
- 8E: research-only gateway/platform registry constraints and dashboard/report manifest presentation, if separately approved.

## Target phase map
| target | candidate | required safety condition |
|---|---|---|
| 8C | metadata, memory/context, tool guardrails, approvals, evidence manifests | Documentation/design plus isolated Saga modules only; tests must stay green. |
| 8D | scheduler dry-runs, session recovery, LLM error taxonomy | No unattended real CloudOps; no unapproved provider fallback; all outputs redacted. |
| 8E | gateway registry/dashboard research | No parallel runtime/gateway unless explicitly approved in a later phase. |
