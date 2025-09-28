from __future__ import annotations

import json
from datetime import datetime, timezone

from llm_cli_core.config import get_config
from llm_cli_core.storage import LocalStorage, TelemetryRecord


def test_local_storage_persists_record(tmp_path):
    config = get_config()
    storage = LocalStorage(config)

    timestamp = datetime.now(timezone.utc)
    record = TelemetryRecord(
        timestamp=timestamp,
        agent_name="test-agent",
        operation="test-operation",
        model="claude-3-5-haiku",
        session_id="session-123",
        user_id="user-123",
        duration_ms=1200,
        total_tokens=150,
        input_tokens=100,
        output_tokens=50,
        cost_usd=0.0025,
        success=True,
        prompt_hash="sha256:abc",
        response_hash="sha256:def",
        metadata={"project": config.project_name, "custom": "value"},
    )

    storage.record(record)

    day_dir = config.resolve_telemetry_dir() / timestamp.strftime("%Y-%m-%d")
    telemetry_file = day_dir / "telemetry.jsonl"
    summary_file = config.resolve_telemetry_dir() / "summary.json"

    assert telemetry_file.exists()
    contents = telemetry_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(contents) == 1
    payload = json.loads(contents[0])
    assert payload["agent_name"] == "test-agent"
    assert payload["tokens"]["total"] == 150
    assert payload["metadata"]["custom"] == "value"

    assert summary_file.exists()
    summary = json.loads(summary_file.read_text(encoding="utf-8"))
    assert summary["total_calls"] == 1
    assert summary["total_cost"] > 0
    assert summary["by_agent"]["test-agent"]["calls"] == 1
