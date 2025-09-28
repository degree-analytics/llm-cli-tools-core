import pytest

from llm_cli_core.config import reset_config_cache


@pytest.fixture(autouse=True)
def telemetry_test_env(tmp_path, monkeypatch):
    telemetry_dir = tmp_path / "telemetry"
    cache_dir = tmp_path / "cache"
    monkeypatch.setenv("LLM_TELEMETRY_DIR", str(telemetry_dir))
    monkeypatch.setenv("LLM_CACHE_DIR", str(cache_dir))
    monkeypatch.delenv("LLM_TELEMETRY_ENABLED", raising=False)
    monkeypatch.delenv("LLM_TELEMETRY_STORAGE_ENABLED", raising=False)
    reset_config_cache()
    yield
    reset_config_cache()
