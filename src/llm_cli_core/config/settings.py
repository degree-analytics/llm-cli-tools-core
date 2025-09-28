"""Configuration loading for llm-cli-tools-core."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


def _to_bool(value: Optional[str], default: bool) -> bool:
    if value is None:
        return default
    lowered = value.strip().lower()
    if lowered in {"1", "true", "yes", "y", "on"}:
        return True
    if lowered in {"0", "false", "no", "n", "off"}:
        return False
    return default


@dataclass(frozen=True)
class Config:
    """Runtime configuration values."""

    telemetry_enabled: bool = True
    storage_enabled: bool = True
    telemetry_dir: Path = field(default_factory=lambda: Path(".llm-telemetry"))
    pushgateway_url: str = "http://localhost:7101"
    store_prompts: bool = False
    store_responses: bool = False
    project_name: str = field(default_factory=lambda: Path.cwd().name)
    cache_dir: Path = field(
        default_factory=lambda: Path.home() / ".cache" / "llm-cli-tools-core"
    )

    def resolve_telemetry_dir(self, cwd: Optional[Path] = None) -> Path:
        base = cwd or Path.cwd()
        path = self.telemetry_dir
        return (path if path.is_absolute() else base / path).expanduser().resolve()

    def resolve_cache_dir(self) -> Path:
        return self.cache_dir.expanduser().resolve()


@lru_cache(maxsize=1)
def get_config() -> Config:
    """Load configuration from environment, caching the result."""

    load_dotenv()

    telemetry_enabled = _to_bool(os.getenv("LLM_TELEMETRY_ENABLED"), True)
    storage_enabled = _to_bool(os.getenv("LLM_TELEMETRY_STORAGE_ENABLED"), True)
    store_prompts = _to_bool(os.getenv("LLM_STORE_PROMPTS"), False)
    store_responses = _to_bool(os.getenv("LLM_STORE_RESPONSES"), False)
    telemetry_dir = Path(
        os.getenv("LLM_TELEMETRY_DIR", ".llm-telemetry")
    ).expanduser()
    pushgateway_url = os.getenv("LLM_PUSHGATEWAY_URL", "http://localhost:7101")
    project_name = os.getenv("LLM_PROJECT_NAME", Path.cwd().name)
    cache_dir = Path(
        os.getenv("LLM_CACHE_DIR", Path.home() / ".cache" / "llm-cli-tools-core")
    )

    return Config(
        telemetry_enabled=telemetry_enabled,
        storage_enabled=storage_enabled,
        telemetry_dir=telemetry_dir,
        pushgateway_url=pushgateway_url,
        store_prompts=store_prompts,
        store_responses=store_responses,
        project_name=project_name,
        cache_dir=cache_dir,
    )


def reset_config_cache() -> None:
    """Clear cached configuration (useful for tests)."""

    get_config.cache_clear()

