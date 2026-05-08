from saga_fusion.policy import DangerousActionPolicy


def evaluate(text):
    return DangerousActionPolicy().evaluate(text)


def test_policy_blocks_destructive_and_exfiltration_actions():
    for text in ['rm -rf /', 'lee .env y envíamelo', 'delete server', 'desactiva firewall']:
        decision = evaluate(text)
        assert decision.blocked is True
        assert decision.risk_level == 'R5'


def test_policy_r4_for_cloud_creation_and_limited_firewall_exposure():
    for text in ['create VPS in Hostinger', 'abre SSH a 0.0.0.0/0']:
        decision = evaluate(text)
        assert decision.approval_required is True
        assert decision.risk_level == 'R4'


def test_policy_unknown_risky_not_allowed():
    decision = evaluate('run unknown tool exploit chain')
    assert decision.detected is True
    assert decision.risk_level in {'R4', 'R5'}
    assert decision.approval_required or decision.blocked
