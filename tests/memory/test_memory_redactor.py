from saga_fusion.memory import MemoryRedactor, MemorySensitivity


def test_redacts_named_tokens_and_fingerprints():
    redactor = MemoryRedactor()
    telegram_key = "TELEGRAM" + "_BOT_TOKEN="
    llm_key = "STRIX_LLM" + "_API_KEY="
    token_value = "123456:" + "abcdefghijklmnopqrstuvwxyz"
    llm_value = "sk-" + "live-secret"
    result = redactor.redact_text(telegram_key + token_value + " " + llm_key + llm_value)
    assert result.sensitivity == MemorySensitivity.SECRET_BLOCKED
    assert "abcdefghijklmnopqrstuvwxyz" not in result.text
    assert "sk-live-secret" not in result.text
    assert "REDACTED" in result.text
    assert result.fingerprints


def test_redacts_authorization_api_keys_cookies_passwords():
    text = "Authorization: Bearer " + "abcdefghijklmnop" + " api_key=" + "abcdef1234567890" + " Cookie: sid=secret password=hunter2"
    result = MemoryRedactor().redact_text(text)
    assert result.secret_blocked is True
    assert "abcdefghijklmnop" not in result.text
    assert "abcdef1234567890" not in result.text
    assert "hunter2" not in result.text
    assert "sid=secret" not in result.text


def test_redacts_env_private_key_and_ssh_paths():
    private_key = "-----BEGIN " + "PRIV" + "ATE KEY-----\nABCDEF\n-----END " + "PRIV" + "ATE KEY-----"
    text = f"load .env and ~/.ssh/id_rsa {private_key}"
    result = MemoryRedactor().redact_text(text)
    assert result.sensitivity == MemorySensitivity.SECRET_BLOCKED
    assert "ABCDEF" not in result.text
    assert ".ssh/id_rsa" not in result.text
    assert ".env" not in result.text or "REDACTED" in result.text
