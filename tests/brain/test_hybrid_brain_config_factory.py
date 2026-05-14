"""Tests for hybrid brain config factory — no API keys exposed, env-agnostic."""

import os
import unittest
from unittest.mock import MagicMock


class TestHybridBrainConfigFactory(unittest.TestCase):

    def setUp(self):
        # Save pristine env
        self._saved = dict(os.environ)
        # Clear all STRIX/DEEPSEEK vars for a clean baseline
        for k in list(os.environ):
            if k.startswith("STRIX_") or k.startswith("DEEPSEEK_"):
                os.environ.pop(k, None)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._saved)

    # ------------------------------------------------------------------
    # BrainConfig repr does not expose API keys
    # ------------------------------------------------------------------

    def test_repr_redacts_api_keys(self):
        from strix.brain.brain_types import BrainConfig, BrainMode, BrainProvider
        bc = BrainConfig(
            mode=BrainMode.hybrid,
            primary_provider=BrainProvider.qwen_local,
            fallback_provider=BrainProvider.deepseek,
            local_api_key="super-secret-local",
            deepseek_api_key="super-secret-ds",
        )
        r = repr(bc)
        self.assertNotIn("super-secret", r)
        self.assertNotIn("api_key", r.lower())

    def test_redacted_dict_redacts_keys(self):
        from strix.brain.brain_types import BrainConfig, BrainMode, BrainProvider
        bc = BrainConfig(
            mode=BrainMode.hybrid,
            primary_provider=BrainProvider.qwen_local,
            fallback_provider=BrainProvider.deepseek,
            local_api_key="super-secret-local",
            deepseek_api_key="super-secret-ds",
        )
        d = bc.redacted_dict()
        self.assertEqual(d["local_api_key"], "[REDACTED]")
        self.assertEqual(d["deepseek_api_key"], "[REDACTED]")

    # ------------------------------------------------------------------
    # Factory builds config even when env vars are missing
    # ------------------------------------------------------------------

    def test_factory_builds_without_env(self):
        from strix.brain.hybrid_brain_config_factory import build_hybrid_llm_config
        LLMConfig_cls = MagicMock(return_value="llm_instance")
        instantiate_fn = lambda cls, **kw: cls(**kw)

        result = build_hybrid_llm_config(LLMConfig_cls, instantiate_fn)

        self.assertIsNotNone(result)
        LLMConfig_cls.assert_called_once()

    def test_factory_returns_instance(self):
        from strix.brain.hybrid_brain_config_factory import build_hybrid_llm_config

        class FakeLLMConfig:
            def __init__(self, **kwargs):
                self.kwargs = kwargs

        instantiate_fn = lambda cls, **kw: cls(**kw)

        result = build_hybrid_llm_config(FakeLLMConfig, instantiate_fn)
        self.assertIsInstance(result, FakeLLMConfig)
        # Provider field carries metadata
        self.assertIn("provider", result.kwargs)

    # ------------------------------------------------------------------
    # Factory uses injected env vars via monkeypatch
    # ------------------------------------------------------------------

    def test_factory_uses_injected_env(self):
        os.environ["STRIX_BRAIN_MODE"] = "deepseek_only"
        os.environ["DEEPSEEK_MODEL"] = "deepseek-coder-v3"
        os.environ["DEEPSEEK_BASE_URL"] = "https://ds.example.com"
        os.environ["DEEPSEEK_API_KEY"] = "ds-key-123"

        from strix.brain.hybrid_brain_config_factory import build_hybrid_llm_config

        class FakeLLMConfig:
            def __init__(self, **kwargs):
                self.kwargs = kwargs

        instantiate_fn = lambda cls, **kw: cls(**kw)

        result = build_hybrid_llm_config(FakeLLMConfig, instantiate_fn)
        self.assertEqual(result.kwargs.get("base_url"), "https://ds.example.com")
        self.assertEqual(result.kwargs.get("model"), "deepseek-coder-v3")

    def test_factory_uses_hybrid_env(self):
        os.environ["STRIX_BRAIN_MODE"] = "hybrid"
        os.environ["STRIX_LOCAL_LLM_BASE_URL"] = "http://local-box:8080/v1"
        os.environ["STRIX_LOCAL_LLM_MODEL"] = "qwen3-7b"
        os.environ["STRIX_LOCAL_LLM_API_KEY"] = "local-key"

        from strix.brain.hybrid_brain_config_factory import build_hybrid_llm_config

        class FakeLLMConfig:
            def __init__(self, **kwargs):
                self.kwargs = kwargs

        instantiate_fn = lambda cls, **kw: cls(**kw)

        result = build_hybrid_llm_config(FakeLLMConfig, instantiate_fn)
        # hybrid → local_first → qwen_local primary
        self.assertEqual(result.kwargs.get("base_url"), "http://local-box:8080/v1")
        self.assertEqual(result.kwargs.get("model"), "qwen3-7b")

    # ------------------------------------------------------------------
    # No .env read, no tokens printed
    # ------------------------------------------------------------------

    def test_no_direct_dotenv_read(self):
        """Factory reads os.environ, not .env files."""
        import inspect
        from strix.brain import brain_config
        src = inspect.getsource(brain_config.load_brain_config)
        self.assertNotIn(".env", src)
        self.assertNotIn("dotenv", src)

    def test_no_token_printed_in_log(self):
        """build_hybrid_llm_config logs mode info, not keys."""
        import logging
        from io import StringIO
        from strix.brain.hybrid_brain_config_factory import build_hybrid_llm_config

        stream = StringIO()
        handler = logging.StreamHandler(stream)
        logging.getLogger("strix.brain.hybrid_brain_config_factory").addHandler(handler)

        class FakeLLMConfig:
            def __init__(self, **kwargs):
                self.kwargs = kwargs

        instantiate_fn = lambda cls, **kw: cls(**kw)

        os.environ["STRIX_LOCAL_LLM_API_KEY"] = "ultra-secret-key-12345"
        build_hybrid_llm_config(FakeLLMConfig, instantiate_fn)

        log_text = stream.getvalue()
        self.assertNotIn("ultra-secret", log_text)
        self.assertNotIn("api_key", log_text.lower())

        logging.getLogger("strix.brain.hybrid_brain_config_factory").removeHandler(handler)

    # ------------------------------------------------------------------
    # No R4/R5 changed
    # ------------------------------------------------------------------

    def test_no_execution_flags_in_factory(self):
        """Factory returns config only — no execution flags."""
        from strix.brain.hybrid_brain_config_factory import build_hybrid_llm_config

        class FakeLLMConfig:
            def __init__(self, **kwargs):
                self.kwargs = kwargs

        instantiate_fn = lambda cls, **kw: cls(**kw)

        result = build_hybrid_llm_config(FakeLLMConfig, instantiate_fn)
        self.assertNotIn("execution_allowed", result.kwargs)
        self.assertNotIn("dry_run", result.kwargs)
        self.assertNotIn("executed", result.kwargs)
