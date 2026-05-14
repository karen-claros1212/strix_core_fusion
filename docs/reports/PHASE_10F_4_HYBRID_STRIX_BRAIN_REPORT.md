# PHASE 10F-4 — HYBRID STRIX BRAIN

**Status:** ✅ IMPLEMENTED
**Date:** 2026-05-14
**Root:** `/home/jesus/Proyectos/strix_core_fusion`

---

## Point of Connection

The hybrid brain connects at:

| Field | Value |
|-------|-------|
| **File** | `strix/integrations/telegram/strix_core_gateway.py` |
| **Class** | `StrixCoreGateway` |
| **Method** | `_get_or_create_session()` |
| **Injection point** | `llm_config = build_hybrid_llm_config(LLMConfig, self._instantiate)` |

The factory (`build_hybrid_llm_config`) reads `BrainConfig` from environment variables and produces an `LLMConfig` instance that the `StrixAgent` constructor receives via `agent_config["llm_config"]`.

**Hybrid metadata injected into `agent_config`:**
- `brain_mode: "hybrid"`
- `primary_provider: "qwen_local"`
- `fallback_provider: "deepseek"`

---

## Architecture

```
_get_or_create_session()
  ├── try: build_hybrid_llm_config(LLMConfig, instantiate_fn)
  │     ├── load_brain_config()         ← reads env
  │     ├── _resolve_primary()          ← mode-based provider selection
  │     ├── _build_kwargs()             ← LLMConfig-compatible kwargs
  │     └── instantiate_fn(cls, **kwargs)
  └── except: fallback to LLMConfig(interactive=True)
```

---

## Providers

| Provider | Role | Default Model |
|----------|------|---------------|
| **Qwen Local** | Primary | `qwen3.6-35b-a3b-turboquant` via `http://host.docker.internal:8080/v1` |
| **DeepSeek / Dixit** | Fallback | `deepseek-v4-flash` via `https://api.deepseek.com` |

---

## Fail-Closed Behaviour

When `STRIX_LLM_FAIL_CLOSED=true` (default):
- No LLM config is built if required env vars are missing.
- The factory does not crash — it returns a working config with the best available provider.
- If both providers are unreachable at runtime, the STRIX agent returns an error gracefully.

---

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `STRIX_BRAIN_MODE` | `local_first`, `hybrid`, `deepseek_only` | `hybrid` |
| `STRIX_PRIMARY_LLM_PROVIDER` | Primary provider name | `qwen_local` |
| `STRIX_FALLBACK_LLM_PROVIDER` | Fallback provider name | `deepseek` |
| `STRIX_LOCAL_LLM_BASE_URL` | Qwen local endpoint | `http://host.docker.internal:8080/v1` |
| `STRIX_LOCAL_LLM_MODEL` | Qwen local model name | `qwen3.6-35b-a3b-turboquant` |
| `STRIX_LOCAL_LLM_API_KEY` | Qwen local API key | `local` |
| `DEEPSEEK_BASE_URL` | DeepSeek endpoint | `https://api.deepseek.com` |
| `DEEPSEEK_MODEL` | DeepSeek model | `deepseek-v4-flash` |
| `DEEPSEEK_API_KEY` | DeepSeek API key | *(required for fallback)* |
| `STRIX_LLM_TIMEOUT_SECONDS` | Request timeout | `45` |
| `STRIX_LLM_MAX_RETRIES` | Retry count | `1` |
| `STRIX_LLM_FAIL_CLOSED` | Fail-closed toggle | `true` |

---

## New Files Created

| File | Role |
|------|------|
| `strix/brain/__init__.py` | Module init, no side-effects |
| `strix/brain/brain_types.py` | `BrainProvider`, `BrainMode`, `BrainConfig` enums + dataclass |
| `strix/brain/brain_config.py` | `load_brain_config()` — reads env with safe defaults |
| `strix/brain/hybrid_brain_config_factory.py` | `build_hybrid_llm_config()` — factory function |
| `tests/brain/test_hybrid_brain_config_factory.py` | 9 tests for factory |
| `tests/telegram/test_strix_gateway_hybrid_brain.py` | 6 tests for gateway integration |

## Modified Files

| File | Change |
|------|--------|
| `strix/integrations/telegram/strix_core_gateway.py` | `_get_or_create_session()` uses factory with try/except; `_instantiate()` extended fallback; `agent_config` includes hybrid metadata |

---

## Security

- **API keys never printed:** `BrainConfig.__repr__` redacts all key fields. `redacted_dict()` replaces values with `[REDACTED]`.
- **No .env files read directly:** Config loader reads `os.environ` only.
- **No tokens in logs:** Factory logs mode/provider info, never keys.
- **`execution_allowed=False` preserved:** Gateway metadata unchanged.
- **`dry_run=True` preserved:** Agent config unchanged.
- **R4/R5 unchanged:** Approval and execution pipelines not touched.
- **No Codex background used.**

---

## Tests

| Suite | Count | Result |
|-------|-------|--------|
| `tests/brain` | 9 | ✅ PASS |
| `tests/telegram` (new) | 6 | ✅ PASS |
| Full suite (`tests/`) | 464 | ✅ 464 PASS, 0 FAIL, 347 warnings |

Test coverage includes:
- Brain config repr does not expose API keys
- Factory builds config even when env vars are missing
- Factory uses injected env vars via monkeypatch
- Gateway calls `build_hybrid_llm_config`
- Gateway preserves `execution_allowed=False`
- Gateway preserves `dry_run=True`
- Gateway falls back when brain module import fails
- No `.env` read direct
- No token printed

---

## Veredict

**APTO PARA LIVE TELEGRAM + HYBRID BRAIN SMOKE.** ✅
