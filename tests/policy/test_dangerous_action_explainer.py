from saga_fusion.policy import DangerousActionExplainer, DangerousActionPolicy


def test_explainer_safe_and_redacted_language_for_r5_and_r4():
    explainer = DangerousActionExplainer()
    blocked = explainer.explain(DangerousActionPolicy().evaluate('rm -rf /'))
    assert 'blocked' in blocked
    assert 'dry-run' in blocked
    r4 = explainer.explain(DangerousActionPolicy().evaluate('create VPS'))
    assert 'requires R4 approval' in r4
    assert 'Sandbox' not in r4 or 'approval' in r4
