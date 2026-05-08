import pytest
from saga_fusion.approval import ApprovalRequestBuilder


def test_builder_creates_unique_ids_stable_hash_and_metadata():
    builder = ApprovalRequestBuilder(expiration_minutes=10)
    payload = {'action_type':'create','target':'VPS'}
    a = builder.build(mission_id='m1', action_payload=payload, canonical_action='create', risk_level='R4', requested_by='user', rollback_plan='rollback', evidence_ref='ev1', now=100)
    b = builder.build(mission_id='m1', action_payload=payload, canonical_action='create', risk_level='R4', requested_by='user', rollback_plan='rollback', evidence_ref='ev1', now=100)
    assert a.approval_id != b.approval_id
    assert a.action_hash == b.action_hash
    assert a.rollback_plan == 'rollback'
    assert a.evidence_ref == 'ev1'
    assert a.expires_at == 700


def test_builder_refuses_r5_and_non_r4():
    builder = ApprovalRequestBuilder()
    with pytest.raises(ValueError):
        builder.build(mission_id='m1', action_payload={}, canonical_action='delete', risk_level='R5', requested_by='u')
    with pytest.raises(ValueError):
        builder.build(mission_id='m1', action_payload={}, canonical_action='status', risk_level='R1', requested_by='u')
