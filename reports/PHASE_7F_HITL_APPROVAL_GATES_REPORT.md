# PHASE 7F — HITL APPROVAL GATES REPORT

## Executive Summary
Phase 7F hardened human-in-the-loop approvals for R4 actions. Approvals are now explicit, identified by approval_id, bound to a deterministic action_hash, expiring, auditable, non-generic, non-reusable, and verified against authorized users. R5 actions remain non-approvable.

## R4 Approval Flow
1. MissionPolicy classifies an action as R4.
2. MissionOperator builds an ApprovalRequest with mission_id, approval_id, action_hash, requested_by, expiry, reason, summary, rollback_plan, before_state, and evidence_ref.
3. ApprovalRequest is stored in ApprovalStore and recorded via ApprovalAudit/EvidenceLogger.
4. `/approve <approval_id>` requires an ID and verifies pending status, expiry, exact action_hash, authorized user, and non-used state.
5. Verified approvals are marked used to prevent replay. No real action is executed in tests.

## R5 Blocking
- R5 never creates ApprovalRequest.
- R5 is blocked by MissionPolicy/DangerousActionPolicy.
- ApprovalRequestBuilder refuses R5.
- ApprovalVerifier blocks R5 request objects if encountered.

## Action Hash
- Action hash is deterministic over canonical JSON payload.
- Hash mismatch sets INVALID_HASH and blocks approval.
- Approval is bound to mission_id/action payload and cannot approve changed actions.

## Expiration / Replay / User Authorization
- ApprovalStore expires old PENDING requests.
- ApprovalVerifier rejects expired approvals.
- Used approvals are rejected as USED/replay-blocked.
- ApprovalVerifier requires approver user_id to be in the authorized user set.

## Evidence
- Approval request creation is recorded in ApprovalAudit and EvidenceLogger.
- Approve/deny verification decisions are recorded.
- Deny records evidence and does not execute anything.
- Audit redacts token-like strings.

## Tests
- `python3 -m pytest tests/approval -q --tb=short`: 7 passed
- `python3 -m pytest tests/policy tests/tool_routing tests/telegram tests/approval -q --tb=short`: 66 passed
- `python3 -m pytest tests -q --tb=short`: 209 passed, 3 warnings

## Residual Risks
- Future 7G reporting should surface approval evidence cleanly in mission reports.
- Future execution adapters must call ApprovalVerifier and SandboxController before any approved R4 dispatch.

## Verdict
APTO PARA 7G REPORTING IMPROVEMENTS: SI
