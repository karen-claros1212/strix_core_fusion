from saga_fusion.llm.llm_config import LLMConfig, load_llm_config, validate_llm_config


def test_llm_config_default_disabled(monkeypatch):
    for key in list(__import__('os').environ):
        if key.startswith('STRIX_LLM_'):
            monkeypatch.delenv(key, raising=False)
    cfg = load_llm_config()
    assert cfg.enabled is False
    assert validate_llm_config(cfg) == (True, [])


def test_llm_config_enabled_requires_base_url(monkeypatch):
    monkeypatch.setenv('STRIX_LLM_ENABLED', 'true')
    monkeypatch.delenv('STRIX_LLM_BASE_URL', raising=False)
    monkeypatch.setenv('STRIX_LLM_MODEL', 'qwen-test')
    cfg = load_llm_config()
    ok, missing = validate_llm_config(cfg)
    assert ok is False
    assert 'STRIX_LLM_BASE_URL' in missing


def test_llm_config_redacts_api_key():
    cfg = LLMConfig(enabled=True, base_url='http://127.0.0.1:8080/v1', model='qwen', api_key='secret-key')
    rendered = cfg.redacted_repr()
    assert 'secret-key' not in rendered
    assert 'REDACTED' in rendered
