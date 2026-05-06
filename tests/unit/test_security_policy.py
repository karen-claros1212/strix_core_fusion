import pytest
from saga_fusion.security_policy import SagaSecurityPolicy

def test_denylist_rm_rf():
    policy = SagaSecurityPolicy()
    action = {'command': 'rm -rf /'}
    decision = policy.evaluate_action(action)
    assert decision.allowed == False
    assert decision.severity == "HIGH" # Ajustado a HIGH según Fase 3.5

def test_denylist_dev_tcp():
    policy = SagaSecurityPolicy()
    action = {'command': 'cat /dev/tcp'}
    decision = policy.evaluate_action(action)
    assert decision.allowed == False

def test_allowlist_ls():
    policy = SagaSecurityPolicy()
    action = {'command': 'ls -la'}
    decision = policy.evaluate_action(action)
    assert decision.allowed == True
    assert decision.severity == "LOW"
