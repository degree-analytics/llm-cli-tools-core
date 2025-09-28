from __future__ import annotations

from datetime import datetime, timezone

from llm_cli_core.analytics import CostFilters, build_cost_report
from llm_cli_core.config import get_config
from llm_cli_core.storage import LocalStorage, TelemetryRecord


class StubPricing:
    def __init__(self, mapping):
        self.mapping = mapping
        self.calls = []

    def estimate_cost(self, model: str, *, input_tokens: int, output_tokens: int):
        self.calls.append((model, input_tokens, output_tokens))
        return self.mapping.get(model.lower())


def _record(storage: LocalStorage, **kwargs):
    now = datetime.now(timezone.utc)
    storage.record(
        TelemetryRecord(
            timestamp=now,
            agent_name=kwargs.get("agent", "doc-finder"),
            operation="search",
            model=kwargs.get("model", "claude-3-5-haiku"),
            session_id="session",
            user_id="user",
            duration_ms=900,
            total_tokens=kwargs.get("total_tokens", 150),
            input_tokens=kwargs.get("input_tokens", 90),
            output_tokens=kwargs.get("output_tokens", 60),
            cost_usd=kwargs.get("cost_usd", 0.0),
            success=kwargs.get("success", True),
            prompt_hash="sha256:aaa",
            response_hash="sha256:bbb",
            metadata={"project": get_config().project_name},
        )
    )


def test_build_cost_report_uses_pricing_when_cost_missing():
    config = get_config()
    storage = LocalStorage(config)
    _record(storage, cost_usd=0.0)

    pricing = StubPricing({"claude-3-5-haiku": 0.123})
    report = build_cost_report(
        config.resolve_telemetry_dir(),
        days=30,
        pricing=pricing,
    )

    assert report["total_cost"] == 0.123
    assert pricing.calls  # ensure estimate_cost was invoked


def test_build_cost_report_filters():
    config = get_config()
    storage = LocalStorage(config)
    _record(storage, agent="doc-finder", success=True, cost_usd=0.1)
    _record(storage, agent="git-info", success=False, cost_usd=0.2)

    pricing = StubPricing({})
    report = build_cost_report(
        config.resolve_telemetry_dir(),
        days=30,
        pricing=pricing,
        filters=CostFilters(status="failure"),
    )

    assert report["total_calls"] == 1
    assert "git-info" in report["by_agent"]
    assert "doc-finder" not in report["by_agent"]
