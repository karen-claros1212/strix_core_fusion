from saga_fusion.approval import ApprovalRequestBuilder, ApprovalStatus, ApprovalStore


def make_request(now=100):
    return ApprovalRequestBuilder(expiration_minutes=1).build(mission_id='m1', action_payload={'a':1}, canonical_action='create', risk_level='R4', requested_by='user', now=now)


def test_store_create_get_approve_deny_used_and_expire():
    store = ApprovalStore()
    req = store.create(make_request())
    assert store.get(req.approval_id) is req
    assert store.mark_approved(req.approval_id) is True
    assert req.status == ApprovalStatus.APPROVED
    assert store.mark_used(req.approval_id) is True
    assert req.used is True
    assert req.status == ApprovalStatus.USED
    req2 = store.create(make_request(now=100))
    assert store.mark_denied(req2.approval_id) is True
    assert req2.status == ApprovalStatus.DENIED
    req3 = store.create(make_request(now=100))
    assert store.expire_old(200) == 1
    assert req3.status == ApprovalStatus.EXPIRED
