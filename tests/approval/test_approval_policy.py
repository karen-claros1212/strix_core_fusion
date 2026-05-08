from saga_fusion.approval import ApprovalPolicy, ApprovalRequestBuilder


def test_policy_risk_requirements_and_expiration():
    policy = ApprovalPolicy()
    assert policy.requires_approval('R4') is True
    assert policy.requires_approval('R3') is False
    assert policy.is_approvable('R5') is False
    req = ApprovalRequestBuilder(expiration_minutes=1).build(mission_id='m1', action_payload={'a':1}, canonical_action='create', risk_level='R4', requested_by='u1', now=100)
    ok, reason = policy.validate_request(req, now=120, authorized_users={'u1'})
    assert ok is True
    assert reason == 'approval_request_valid'
    ok, reason = policy.validate_request(req, now=200, authorized_users={'u1'})
    assert ok is False
    assert reason == 'approval_expired'
