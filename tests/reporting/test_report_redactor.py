from saga_fusion.reporting import ReportRedactor


def test_report_redactor_redacts_tokens_keys_auth_private_key_and_preserves_fingerprint():
    telegram_value = '123456789:' + 'ABCDEFGHIJKLMNOPQRSTUVwx-yz'
    bearer_value = 'abc' + '.def' + '.ghi'
    private_key = '-----BEGIN RSA ' + 'PRIV' + 'ATE KEY-----abc-----END RSA ' + 'PRIV' + 'ATE KEY-----'
    text = f'''
TELEGRAM_BOT_TOKEN={telegram_value}
STRIX_LLM_API_KEY=secret-value
Authorization: Bearer {bearer_value}
{private_key}
fingerprint: SHA256:AA:BB:CC:DD:EE:FF:00:11
'''
    redacted = ReportRedactor().redact(text)
    assert 'secret-value' not in redacted
    assert 'abc.def.ghi' not in redacted
    assert 'PRIVATE KEY-----abc' not in redacted
    assert 'TELEGRAM_BOT_TOKEN=[REDACTED]' in redacted
    assert 'STRIX_LLM_API_KEY=[REDACTED]' in redacted
    assert 'Authorization: Bearer [REDACTED]' in redacted
    assert 'fingerprint: SHA256:AA:BB:CC:DD:EE:FF:00:11' in redacted
