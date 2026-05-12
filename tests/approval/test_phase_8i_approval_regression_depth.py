import asyncio
import json

from saga_fusion.approval import (
    ApprovalAudit,
    ApprovalRegressionMatrix,
    ApprovalRequest,
    ApprovalRequestBuilder,
    ApprovalRiskLevel,
    ApprovalStatus,
    ApprovalStore,
    ApprovalVerifier,
)
from saga_fusion.telegram.mission_operator import TelegramMissionOperator
from saga_fusion.telegram.mock_telegram_adapter import MockTelegramAdapter
from saga_fusion.telegram.telegram_config import TelegramConfig


def _stored_request(now=100.0, ttl_minutes=1):
    builder = ApprovalRequestBuilder(expiration_minutes=ttl_minutes)
    store = ApprovalStore()
    req = store.create(
        builder.build(
            mission_id="mission-r4",
            action_payload={"action_type": "create", "target": "vps"},
            canonical_action="create",
            risk_level="R4",
            requested_by="operator",
            now=now,
        )
    )
    return store, req


def test_phase_8i_expiry_boundary_just_before_ok_at_and_after_blocked():
    store, req = _stored_request(now=100.0, ttl_minutes=1)
    verifier = ApprovalVerifier(store)

    just_before = verifier.verify(
        req.approval_id,
        action_hash=req.action_hash,
        user_id="operator",
        authorized_users={"operator"},
        now=req.expires_at - 0.001,
    )
    assert just_before.allowed is True
    assert just_before.status == ApprovalStatus.APPROVED
    assert just_before.evidence["execution_allowed"] is False

    at_store, at_req = _stored_request(now=100.0, ttl_minutes=1)
    at_expiry = ApprovalVerifier(at_store).verify(
        at_req.approval_id,
        action_hash=at_req.action_hash,
        user_id="operator",
        authorized_users={"operator"},
        now=at_req.expires_at,
    )
    assert at_expiry.allowed is False
    assert at_expiry.status == ApprovalStatus.EXPIRED
    assert at_req.status == ApprovalStatus.EXPIRED

    after_store, after_req = _stored_request(now=100.0, ttl_minutes=1)
    after_expiry = ApprovalVerifier(after_store).verify(
        after_req.approval_id,
        action_hash=after_req.action_hash,
        user_id="operator",
        authorized_users={"operator"},
        now=after_req.expires_at + 1,
    )
    assert after_expiry.status == ApprovalStatus.EXPIRED


def test_phase_8i_replay_hash_mismatch_unauthorized_and_denied_are_blocked():
    store, req = _stored_request()
    verifier = ApprovalVerifier(store)
    ok = verifier.verify(req.approval_id, action_hash=req.action_hash, user_id="operator", authorized_users={"operator"}, now=120)
    assert ok.allowed is True
    assert store.mark_used(req.approval_id) is True
    replay = verifier.verify(req.approval_id, action_hash=req.action_hash, user_id="operator", authorized_users={"operator"}, now=121)
    assert replay.status == ApprovalStatus.USED
    assert replay.reason == "approval_replay_blocked"
    assert replay.evidence["execution_allowed"] is False

    mismatch_store, mismatch_req = _stored_request()
    mismatch = ApprovalVerifier(mismatch_store).verify(mismatch_req.approval_id, action_hash="wrong", user_id="operator", authorized_users={"operator"}, now=120)
    assert mismatch.status == ApprovalStatus.INVALID_HASH
    assert mismatch.reason == "action_hash_mismatch"
    assert mismatch_req.status == ApprovalStatus.INVALID_HASH
    still_blocked = ApprovalVerifier(mismatch_store).verify(mismatch_req.approval_id, action_hash=mismatch_req.action_hash, user_id="operator", authorized_users={"operator"}, now=121)
    assert still_blocked.status == ApprovalStatus.INVALID_HASH
    assert still_blocked.allowed is False

    unauthorized_store, unauthorized_req = _stored_request()
    unauthorized = ApprovalVerifier(unauthorized_store).verify(unauthorized_req.approval_id, action_hash=unauthorized_req.action_hash, user_id="intruder", authorized_users={"operator"}, now=120)
    assert unauthorized.status == ApprovalStatus.BLOCKED
    assert unauthorized.reason == "approver_not_authorized"
    assert unauthorized_req.status == ApprovalStatus.PENDING

    denied_store, denied_req = _stored_request()
    assert denied_store.mark_denied(denied_req.approval_id) is True
    denied = ApprovalVerifier(denied_store).verify(denied_req.approval_id, action_hash=denied_req.action_hash, user_id="operator", authorized_users={"operator"}, now=120)
    assert denied.status == ApprovalStatus.DENIED
    assert denied.reason == "approval_denied_irreversible"


def test_phase_8i_nonexistent_and_r5_approval_attempts_are_blocked_without_execution():
    missing = ApprovalVerifier(ApprovalStore()).verify("missing", action_hash="hash", user_id="operator", authorized_users={"operator"}, now=120)
    assert missing.status == ApprovalStatus.BLOCKED
    assert missing.reason == "approval_not_found"
    assert missing.evidence["execution_allowed"] is False

    store = ApprovalStore()
    r5 = store.create(
        ApprovalRequest(
            "r5-approval-id",
            "mission-r5",
            "hash",
            "delete",
            ApprovalRiskLevel.R5,
            "operator",
            100,
            200,
            "blocked",
            "blocked",
            "none",
            "none",
            "mission:mission-r5",
        )
    )
    decision = ApprovalVerifier(store).verify(r5.approval_id, action_hash="hash", user_id="operator", authorized_users={"operator"}, now=120)
    assert decision.status == ApprovalStatus.BLOCKED
    assert decision.reason == "r5_not_approvable"
    assert decision.evidence["execution_allowed"] is False


def test_phase_8i_audit_summary_redacts_sensitive_values():
    audit = ApprovalAudit()
    audit.record(
        "approval_verified",
        {
            "approval_id": "approval-1",
            "token": "github_pat_" + "A" * 24,
            "detail": "api_key=" + "supersecretvalue",
            "nested": {"password": "password=" + "letmein123"},
        },
    )
    summary = audit.summary()
    rendered = json.dumps(summary, sort_keys=True)
    assert "github_pat_" not in rendered
    assert "supersecretvalue" not in rendered
    assert "letmein123" not in rendered
    assert "[REDACTED]" in rendered
    assert summary["execution_allowed"] is False
    assert summary["contains_sensitive_values"] is False


def test_phase_8i_regression_matrix_covers_required_security_cases():
    manifest = ApprovalRegressionMatrix().to_manifest()
    cases = {case["case_id"]: case for case in manifest["cases"]}
    assert manifest["execution_allowed"] is False
    for case_id in {
        "r4_valid_non_executing",
        "r5_non_approvable",
        "expired_at_ttl",
        "replay_used",
        "hash_mismatch",
        "unauthorized_actor",
        "denied_irreversible",
        "nonexistent_approval",
    }:
        assert case_id in cases
        assert cases[case_id]["execution_allowed"] is False
        assert cases[case_id]["real_execution"] is False


def test_phase_8i_telegram_approval_success_is_non_executing_and_replay_is_used():
    async def run():
        cfg = TelegramConfig(mode="mock", allowed_user_ids=["operator"])
        operator = TelegramMissionOperator(cfg, MockTelegramAdapter(cfg))
        r4 = json.loads(await operator.handle_message("chat", "operator", "Crea un VPS en Hostinger"))
        approval_id = r4["approval_id"]
        action_hash = r4["action_hash"]
        approved = json.loads(await operator.handle_message("chat", "operator", f"/approve {approval_id} {action_hash}"))
        assert approved["status"] == "approved"
        assert approved["reason"] == "approval_verified_non_executing"
        assert approved["executed"] is False
        assert operator.approval_store.get(approval_id).status == ApprovalStatus.USED
        replay = json.loads(await operator.handle_message("chat", "operator", f"/approve {approval_id} {action_hash}"))
        assert replay["status"] == "used"
        assert replay["reason"] == "approval_replay_blocked"
        assert replay["executed"] is False

    asyncio.run(run())


def test_phase_8i_telegram_r5_creates_no_approval_and_nonexistent_approval_blocked():
    async def run():
        cfg = TelegramConfig(mode="mock", allowed_user_ids=["operator"])
        operator = TelegramMissionOperator(cfg, MockTelegramAdapter(cfg))
        r5 = json.loads(await operator.handle_message("chat", "operator", "Elimina el servidor y borra backups"))
        assert r5["status"] == "blocked"
        assert r5["approval_id"] is None
        assert operator.approval_store.get(r5.get("approval_id")) is None
        blocked = json.loads(await operator.handle_message("chat", "operator", "/approve nonexistent hash"))
        assert blocked["status"] == "blocked"
        assert blocked["reason"] == "approval_not_found"
        assert blocked["executed"] is False

    asyncio.run(run())
