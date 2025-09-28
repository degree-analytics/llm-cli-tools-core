"""Local JSONL-based storage backend."""

from __future__ import annotations

import json
from datetime import timezone
from pathlib import Path
from typing import Any, Dict

from filelock import FileLock

from llm_cli_core.config import Config

from .base import StorageBackend, TelemetryRecord


class LocalStorage(StorageBackend):
    """Persist telemetry to JSONL files on the local filesystem."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.base_dir = config.resolve_telemetry_dir()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def record(self, record: TelemetryRecord) -> None:
        timestamp = record.timestamp.astimezone(timezone.utc)
        date_dir = self.base_dir / timestamp.strftime("%Y-%m-%d")
        date_dir.mkdir(parents=True, exist_ok=True)

        telemetry_path = date_dir / "telemetry.jsonl"
        prompts_path = date_dir / "prompts.jsonl"
        responses_path = date_dir / "responses.jsonl"
        summary_path = self.base_dir / "summary.json"

        payload = self._build_payload(record, timestamp.isoformat())
        self._append_jsonl(telemetry_path, payload)
        self._update_summary(summary_path, payload)

        if self.config.store_prompts and record.prompt_text:
            self._append_jsonl(
                prompts_path,
                {
                    "timestamp": payload["timestamp"],
                    "agent_name": record.agent_name,
                    "operation": record.operation,
                    "prompt_hash": record.prompt_hash,
                    "prompt": record.prompt_text,
                },
            )

        if self.config.store_responses and record.response_text:
            self._append_jsonl(
                responses_path,
                {
                    "timestamp": payload["timestamp"],
                    "agent_name": record.agent_name,
                    "operation": record.operation,
                    "response_hash": record.response_hash,
                    "response": record.response_text,
                },
            )

    def _append_jsonl(self, path: Path, payload: Dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        lock = FileLock(str(path) + ".lock")
        with lock:
            with path.open("a", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False)
                handle.write("\n")

    def _update_summary(self, path: Path, payload: Dict[str, Any]) -> None:
        lock = FileLock(str(path) + ".lock")
        with lock:
            if path.exists():
                summary = json.loads(path.read_text(encoding="utf-8"))
            else:
                summary = {
                    "total_cost": 0.0,
                    "total_calls": 0,
                    "total_tokens": {
                        "input": 0,
                        "output": 0,
                        "total": 0,
                    },
                    "by_model": {},
                    "by_agent": {},
                    "by_status": {"success": 0, "failure": 0},
                }

            cost = payload.get("cost_usd", 0.0) or 0.0
            tokens = payload.get("tokens", {})
            input_tokens = tokens.get("input", 0) or 0
            output_tokens = tokens.get("output", 0) or 0
            total_tokens = tokens.get("total", input_tokens + output_tokens) or 0
            success = bool(payload.get("success", True))
            agent = payload.get("agent_name", "unknown")
            model = payload.get("model", "unknown")

            summary["total_calls"] += 1
            summary["total_cost"] = round(summary["total_cost"] + cost, 10)
            summary["total_tokens"]["input"] += input_tokens
            summary["total_tokens"]["output"] += output_tokens
            summary["total_tokens"]["total"] += total_tokens

            summary["by_model"].setdefault(model, {"calls": 0, "cost_usd": 0.0, "tokens": 0})
            summary["by_model"][model]["calls"] += 1
            summary["by_model"][model]["cost_usd"] = round(
                summary["by_model"][model]["cost_usd"] + cost, 10
            )
            summary["by_model"][model]["tokens"] += total_tokens

            summary["by_agent"].setdefault(
                agent, {"calls": 0, "cost_usd": 0.0, "tokens": 0}
            )
            summary["by_agent"][agent]["calls"] += 1
            summary["by_agent"][agent]["cost_usd"] = round(
                summary["by_agent"][agent]["cost_usd"] + cost, 10
            )
            summary["by_agent"][agent]["tokens"] += total_tokens

            key = "success" if success else "failure"
            summary["by_status"][key] = summary["by_status"].get(key, 0) + 1

            path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    def _build_payload(self, record: TelemetryRecord, timestamp: str) -> Dict[str, Any]:
        return {
            "timestamp": timestamp,
            "agent_name": record.agent_name,
            "operation": record.operation,
            "model": record.model,
            "session_id": record.session_id,
            "user_id": record.user_id,
            "duration_ms": record.duration_ms,
            "tokens": {
                "input": record.input_tokens,
                "output": record.output_tokens,
                "total": record.total_tokens,
            },
            "cost_usd": record.cost_usd,
            "success": record.success,
            "prompt_hash": record.prompt_hash,
            "response_hash": record.response_hash,
            "metadata": record.metadata,
        }

