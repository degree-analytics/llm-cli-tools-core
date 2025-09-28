from __future__ import annotations

import json
from datetime import datetime, timezone

from llm_cli_core.cli import main
from llm_cli_core.config import get_config
from llm_cli_core.storage import LocalStorage, TelemetryRecord


def _make_record(cost: float = 0.01) -> TelemetryRecord:
    now = datetime.now(timezone.utc)
    return TelemetryRecord(
        timestamp=now,
        agent_name="doc-finder",
        operation="search",
        model="claude-3-5-haiku",
        session_id="session",
        user_id="user",
        duration_ms=800,
        total_tokens=120,
        input_tokens=70,
        output_tokens=50,
        cost_usd=cost,
        success=True,
        prompt_hash="sha256:aaa",
        response_hash="sha256:bbb",
        metadata={"project": get_config().project_name},
    )


def test_cli_costs_json_output(capsys):
    config = get_config()
    storage = LocalStorage(config)
    storage.record(_make_record())

    exit_code = main(["costs", "--json"])
    assert exit_code == 0

    captured = capsys.readouterr()
    data = json.loads(captured.out.strip())
    assert data["total_calls"] == 1
    assert data["by_agent"]["doc-finder"]["calls"] == 1


def test_cli_costs_table_output(capsys):
    config = get_config()
    storage = LocalStorage(config)
    storage.record(_make_record())

    exit_code = main(["costs"])
    assert exit_code == 0

    captured = capsys.readouterr().out
    assert "Telemetry Cost Report" in captured
    assert "Total cost" in captured


def test_cli_costs_no_records(capsys):
    config = get_config()
    config.resolve_telemetry_dir().mkdir(parents=True, exist_ok=True)

    exit_code = main(["costs"])
    assert exit_code == 0

    captured = capsys.readouterr().out
    assert "No telemetry records" in captured


def test_cli_costs_missing_directory(tmp_path, capsys):
    exit_code = main(["costs", "--path", str(tmp_path / "missing")])
    assert exit_code == 1
    message = capsys.readouterr().out
    assert "Telemetry directory not found" in message
