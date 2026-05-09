# Hermes Pattern Integration Architecture — STRIX Clean-Room Plan

## Boundary
Hermes Agent is an external reference only. The audited checkout lives at `external_sources/hermes-agent` and is ignored by git. STRIX must not import, execute, vendor, or copy from it.

## Authoritative STRIX controls
- `MissionPolicy` and `DangerousActionPolicy` classify and block unsafe intent.
- `ToolRouter` and `ToolRoutePolicy` create declarative execution plans only.
- `ApprovalVerifier` gates R4 with approval IDs and exact action hashes.
- `SandboxController` remains the only execution boundary.
- `EvidenceLogger`, `Reporting`, and secret redactors remain mandatory for user-visible and stored outputs.
- Memory/context is non-authoritative and cannot override policy.

## Clean-room adaptation lanes
1. **Phase 8C — Control-plane hardening**
   - Add STRIX extension/workflow metadata schema.
   - Add context-compression templates and memory-context streaming scrubber tests.
   - Add tool-loop guardrail counters for repeated failures/no-progress.
   - Add approval timeout-to-deny and evidence manifest regressions.
2. **Phase 8D — Operational resilience**
   - Add dry-run scheduled audit specifications.
   - Add Telegram session recovery and restart/pending-drain audit model.
   - Add LLM error taxonomy and bounded retry reporting.
3. **Phase 8E — Research only**
   - Evaluate platform registry/dashboard manifest constraints without creating a parallel gateway or runtime.

## Prohibited integration paths
- No Hermes gateway/platform registry in STRIX runtime.
- No Hermes plugin host, provider plugins, skills, or self-improvement loops.
- No installer/dependency reuse.
- No automatic credential rotation or provider fallback.
- No real-token or `.env` access.

## Evidence requirements for future phases
Every future Hermes-inspired implementation must include: source-pattern citation by path, clean-room design note, risk classification, tests, redaction behavior, and full-suite result.
