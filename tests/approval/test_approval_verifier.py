from saga_fusion.approval import ApprovalRequestBuilder, ApprovalStatus, ApprovalStore, ApprovalVerifier, ApprovalRequest, ApprovalRiskLevel


def setup_request(now=100):
    builder = ApprovalRequestBuilder(expiration_minutes=1)
    store = ApprovalStore()
    req = store.create(builder.build(mission_id='m1', action_payload={'a':1}, canonical_action='create', risk_level='R4', requested_by='requester', now=now))
    return store, req


def test_verifier_valid_expired_used_hash_user_missing_and_r5():
    store, req = setup_request()
    verifier = ApprovalVerifier(store)
    ok = verifier.verify(req.approval_id, action_hash=req.action_hash, user_id='u1', authorized_users={'u1'}, now=120)
    assert ok.allowed is True
    store.mark_used(req.approval_id)
    replay = verifier.verify(req.approval_id, action_hash=req.action_hash, user_id='u1', authorized_users={'u1'}, now=121)
    assert replay.allowed is False
    assert replay.status == ApprovalStatus.USED

    store2, expired = setup_request()
    expired_decision = ApprovalVerifier(store2).verify(expired.approval_id, action_hash=expired.action_hash, user_id='u1', authorized_users={'u1'}, now=200)
    assert expired_decision.status == ApprovalStatus.EXPIRED

    store3, changed = setup_request()
    mismatch = ApprovalVerifier(store3).verify(changed.approval_id, action_hash='bad-hash', user_id='u1', authorized_users={'u1'}, now=120)
    assert mismatch.status == ApprovalStatus.INVALID_HASH

    store4, unauth = setup_request()
    blocked = ApprovalVerifier(store4).verify(unauth.approval_id, action_hash=unauth.action_hash, user_id='bad', authorized_users={'u1'}, now=120)
    assert blocked.status == ApprovalStatus.BLOCKED

    missing = ApprovalVerifier(ApprovalStore()).verify('missing', action_hash='x', user_id='u1', authorized_users={'u1'}, now=120)
    assert missing.status == ApprovalStatus.BLOCKED

    r5 = ApprovalRequest('a-r5','m2','hash','delete',ApprovalRiskLevel.R5,'u',100,200,'r5','summary','rollback','before','evidence')
    store5 = ApprovalStore(); store5.create(r5)
    r5_decision = ApprovalVerifier(store5).verify('a-r5', action_hash='hash', user_id='u1', authorized_users={'u1'}, now=120)
    assert r5_decision.status == ApprovalStatus.BLOCKED
