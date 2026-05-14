"""
Hybrid brain LLM config factory.

Builds an ``LLMConfig`` instance suitable for STRIX agent sessions,
preferring a local Qwen model with a remote DeepSeek fallback.

Usage (from within StrixCoreGateway)::

    from strix.brain.hybrid_brain_config_factory import build_hybrid_llm_config
    llm_config = build_hybrid_llm_config(LLMConfig, self._instantiate)
    agent_config = {"llm_config": llm_config, ...}
"""

from __future__ import annotations

import logging
from typing import Any, Callable

from strix.brain.brain_config import load_brain_config
from strix.brain.brain_types import BrainConfig, BrainMode, BrainProvider

_log = logging.getLogger(__name__)


def build_hybrid_llm_config(
    LLMConfig_cls: type,
    instantiate_fn: Callable[..., Any],
    brain_config: BrainConfig | None = None,
) -> Any:
    """Return an ``LLMConfig`` instance configured for the current brain mode.

    Parameters
    ----------
    LLMConfig_cls
        The ``LLMConfig`` class (e.g. from saga_fusion/llm or strix).
    instantiate_fn
        A callable that creates instances (e.g. ``StrixCoreGateway._instantiate``).
    brain_config
        Optional pre-loaded ``BrainConfig``.  When ``None`` the factory calls
        ``load_brain_config()`` to read environment variables.

    Returns
    -------
    An ``LLMConfig`` instance — never ``None``.
    """
    bc = brain_config if brain_config is not None else load_brain_config()

    # -- decide which provider to use as the "primary" LLMConfig ---------------
    provider_url, provider_model, provider_key = _resolve_primary(bc)

    # -- build kwargs with the fields LLMConfig is most likely to accept ------
    kwargs = _build_kwargs(provider_url, provider_model, provider_key, bc)

    _log.info("build_hybrid_llm_config: mode=%s primary=%s fallback=%s model=%s",
              bc.mode.value, bc.primary_provider.value, bc.fallback_provider.value, bc.local_model)

    # -- delegate to instantiate_fn (which has its own fallback chain) --------
    return instantiate_fn(LLMConfig_cls, **kwargs)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _resolve_primary(bc: BrainConfig) -> tuple[str, str, str]:
    """Return (base_url, model, api_key) for the primary provider."""
    if bc.mode == BrainMode.deepseek_only or (
        bc.mode == BrainMode.hybrid and bc.primary_provider == BrainProvider.deepseek
    ):
        return bc.deepseek_base_url, bc.deepseek_model, bc.deepseek_api_key
    # local_first or hybrid with qwen primary
    return bc.local_base_url, bc.local_model, bc.local_api_key


def _build_kwargs(
    base_url: str,
    model: str,
    api_key: str,
    bc: BrainConfig,
) -> dict[str, Any]:
    """Assemble keyword arguments that ``LLMConfig`` is likely to accept.

    Extra keys (``interactive``, etc.) are included so that test fakes and
    minimal config classes still receive them; the caller's ``_instantiate``
    fallback chain silently drops incompatible kwargs.
    """
    provider_value = (
        f"hybrid:{bc.primary_provider.value}:{bc.fallback_provider.value}"
        if bc.mode in (BrainMode.hybrid, BrainMode.local_first)
        else bc.primary_provider.value
    ) if bc.mode != BrainMode.deepseek_only else "deepseek"

    kwargs: dict[str, Any] = {
        "base_url": base_url,
        "model": model,
        "api_key": api_key,
        "timeout_seconds": bc.timeout_seconds,
        "provider": provider_value,
        "interactive": True,
    }

    # Optional fields that real LLMConfig may or may not expose
    _try_set(kwargs, "max_output_tokens", 2048)
    _try_set(kwargs, "temperature", 0.2)
    _try_set(kwargs, "enabled", True)

    return kwargs


def _try_set(kwargs: dict[str, Any], key: str, value: Any) -> None:
    """Set *key* only when it is not already present (caller can override)."""
    kwargs.setdefault(key, value)
