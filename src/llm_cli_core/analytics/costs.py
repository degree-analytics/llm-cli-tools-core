"""Cost analytics helpers."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Optional

from llm_cli_core.storage.readers import iter_telemetry_records


@dataclass
class CostFilters:
    project: Optional[str] = None
    agent: Optional[str] = None
    model: Optional[str] = None
    status: Optional[str] = None


def build_cost_report(
    base_dir: Path,
    *,
    days: int,
    pricing,
    filters: Optional[CostFilters] = None,
    now: Optional[datetime] = None,
) -> Dict[str, object]:
    """Aggregate cost metrics for telemetry records."""

    filters = filters or CostFilters()
    now = now or datetime.now(timezone.utc)
    start = now - timedelta(days=days)

    total_cost = 0.0
    total_calls = 0
    total_input_tokens = 0
    total_output_tokens = 0

    by_model: Dict[str, Dict[str, object]] = {}
    by_agent: Dict[str, Dict[str, object]] = {}

    for record in iter_telemetry_records(base_dir, start, now):
        if not _matches_filters(record, filters):
            continue

        tokens = record.get("tokens") or {}
        input_tokens = int(tokens.get("input", 0) or 0)
        output_tokens = int(tokens.get("output", 0) or 0)
        total_tokens = int(tokens.get("total", input_tokens + output_tokens) or 0)

        cost = record.get("cost_usd")
        if cost in (None, 0, 0.0):
            model_name = str(record.get("model", "")).strip()
            cost_estimate = pricing.estimate_cost(
                model_name,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )
            cost = cost_estimate if cost_estimate is not None else 0.0
        else:
            cost = float(cost)

        total_calls += 1
        total_cost += cost
        total_input_tokens += input_tokens
        total_output_tokens += output_tokens

        model_key = str(record.get("model", "unknown")) or "unknown"
        agent_key = str(record.get("agent_name", "unknown")) or "unknown"

        _accumulate(by_model, model_key, cost, total_tokens, input_tokens, output_tokens)
        _accumulate(by_agent, agent_key, cost, total_tokens, input_tokens, output_tokens)

    return {
        "total_cost": round(total_cost, 6),
        "total_calls": total_calls,
        "total_tokens": {
            "input": total_input_tokens,
            "output": total_output_tokens,
            "total": total_input_tokens + total_output_tokens,
        },
        "currency": "USD",
        "by_model": _finalize_sections(by_model),
        "by_agent": _finalize_sections(by_agent),
        "filters": {k: v for k, v in asdict(filters).items() if v is not None},
        "window": {
            "start": start.isoformat(),
            "end": now.isoformat(),
            "days": days,
        },
    }


def _matches_filters(record: Dict[str, object], filters: CostFilters) -> bool:
    if filters.project:
        metadata = record.get("metadata") or {}
        project = metadata.get("project") if isinstance(metadata, dict) else None
        if not project or project.lower() != filters.project.lower():
            return False

    if filters.agent:
        agent = record.get("agent_name")
        if not agent or str(agent).lower() != filters.agent.lower():
            return False

    if filters.model:
        model = record.get("model")
        if not model or str(model).lower() != filters.model.lower():
            return False

    if filters.status:
        status = str(filters.status).lower()
        success = bool(record.get("success", True))
        if status == "success" and not success:
            return False
        if status == "failure" and success:
            return False

    return True


def _accumulate(
    section: Dict[str, Dict[str, object]],
    key: str,
    cost: float,
    total_tokens: int,
    input_tokens: int,
    output_tokens: int,
) -> None:
    entry = section.setdefault(
        key,
        {
            "cost_usd": 0.0,
            "calls": 0,
            "tokens": {"total": 0, "input": 0, "output": 0},
        },
    )
    entry["cost_usd"] = round(entry["cost_usd"] + cost, 6)
    entry["calls"] += 1
    tokens = entry["tokens"]
    tokens["total"] += total_tokens
    tokens["input"] += input_tokens
    tokens["output"] += output_tokens


def _finalize_sections(section: Dict[str, Dict[str, object]]) -> Dict[str, Dict[str, object]]:
    return dict(sorted(section.items(), key=lambda item: item[1]["cost_usd"], reverse=True))

