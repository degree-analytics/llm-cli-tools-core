from __future__ import annotations

from datetime import datetime, timezone, timedelta

from llm_cli_core.config import get_config
from llm_cli_core.models.pricing import ModelPricing, PricingCache


def test_pricing_cache_loads_and_uses_cache(monkeypatch):
    config = get_config()
    cache = PricingCache(config)

    fetched_at = datetime.now(timezone.utc)

    def fake_fetch(self):  # noqa: D401
        models = {
            "anthropic.claude-3-5-haiku": ModelPricing(prompt=8e-7, completion=4e-6)
        }
        return models, fetched_at

    monkeypatch.setattr(PricingCache, "_fetch_remote", fake_fetch, raising=False)

    models = cache.load(force=True)
    assert "anthropic.claude-3-5-haiku" in models
    assert cache.cache_path.exists()

    # Estimation should resolve using substring match
    estimate = cache.estimate_cost(
        "claude-3-5-haiku-20241022",
        input_tokens=1000,
        output_tokens=500,
    )
    assert estimate and estimate > 0

    # Subsequent loads should reuse cache without refetching
    called = False

    def fail_fetch(self):
        nonlocal called
        called = True
        raise AssertionError("fetch should not be called")

    monkeypatch.setattr(PricingCache, "_fetch_remote", fail_fetch, raising=False)
    cache._models = {}
    cache._fetched_at = fetched_at
    cache.load()
    assert called is False


def test_pricing_cache_detects_stale(monkeypatch):
    config = get_config()
    cache = PricingCache(config)

    old_time = datetime.now(timezone.utc) - timedelta(days=8)

    def fake_fetch(self):
        models = {"gpt-4": ModelPricing(prompt=3e-6, completion=6e-6)}
        return models, datetime.now(timezone.utc)

    cache._models = {"gpt-4": ModelPricing(prompt=3e-6, completion=6e-6)}
    cache._fetched_at = old_time

    monkeypatch.setattr(PricingCache, "_fetch_remote", fake_fetch, raising=False)
    cache.load()
    assert cache._fetched_at is not None
    assert cache._fetched_at > old_time
