# Phase 8I — Approval Timeout + Regression Depth Report

## Status
COMPLETED — STRIX-owned approval timeout and HITL regression hardening was implemented without adding any real execution path.

## Scope
- Hardened `saga_fusion/approval/` timeout, terminal-state, verifier evidence, and regression metadata behavior.
- Added approval regression depth tests under `tests/approval/` and preserved existing Telegram approval flow compatibility.
- Kept R4 as the only approvable HITL risk level.
- Kept R5 non-approvable/blocked and ensured R5 missions create no approval.

## Implementation
- `ApprovalRequest` now exposes deterministic expiry helpers:
  - `is_expired(now)` returns true at or after `expires_at`.
  - `seconds_until_expiry(now)` returns bounded evidence metadata.
  - `is_terminal` identifies used/denied/expired/hash-invalid/blocked approvals.
- `ApprovalStore` now preserves terminal-state safety:
  - Deny/approve only applies to pending unused approvals.
  - Used approvals are marked non-replayable.
  - Expiry is enforced at and after the TTL boundary.
- `ApprovalVerifier` now emits deterministic non-executing decisions for:
  - missing approval IDs,
  - R5 approval attempts,
  - expired approvals,
  - used/replay attempts,
  - hash mismatch,
  - unauthorized actor,
  - denied/terminal approvals,
  - successful R4 approval verification.
- `ApprovalVerifier` evidence always carries `execution_allowed=False`.
- `ApprovalAudit.summary()` returns redacted, evidence-safe summary metadata.
- `ApprovalRegressionMatrix` provides metadata-only coverage for R4, R5, expired, replay, hash mismatch, unauthorized user, denial, and nonexistent-ID cases.

## Security Gates
- No Hermes code copy, execution, runtime, gateway, plugin host, or toolset integration.
- No Agent Zero, OpenCLAW, installed Hermes, Qwen, TurboQuant, llama.cpp, or WSL2 changes.
- No real Telegram, CloudOps, external pentest, token, or `.env` change.
- No direct execution added; approval success remains non-executing and Telegram approval responses return `executed=False`.
- `SandboxController` remains the execution boundary.
- R4 remains approval-required; R5 remains blocked/non-approvable.
- Old untracked Phase 6B-4 reports/logs and `external_sources/` were not staged.

## Tests
- `python3 -m pytest tests/approval -q --tb=short` → `14 passed`
- `python3 -m pytest tests/approval tests/telegram tests/manifests -q --tb=short` → `69 passed`
- `python3 -m pytest tests -q --tb=short` → `334 passed, 3 warnings`

Warnings are the existing coroutine warnings in integration/security tests and are not introduced by Phase 8I.

## Verdict
Phase 8I closes the planned Hermes-inspired approval timeout/regression lane. STRIX may proceed to Phase 9 original STRIX optimization or Phase 8 closure, with the same hard boundaries: no production execution without SandboxController, R4 HITL approval, and R5 non-approvable blocking.
