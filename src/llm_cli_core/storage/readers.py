"""Utilities for reading telemetry storage."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Iterator, Optional

ISO_Z_SUFFIX = "Z"


def _parse_timestamp(value: str) -> datetime:
    if value.endswith(ISO_Z_SUFFIX):
        value = value.replace(ISO_Z_SUFFIX, "+00:00")
    return datetime.fromisoformat(value)


def iter_telemetry_records(
    base_dir: Path,
    start: datetime,
    end: datetime,
    *,
    limit: Optional[int] = None,
) -> Iterator[Dict[str, object]]:
    """Yield telemetry records within the provided time window."""

    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    if end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)

    current = start.date()
    end_date = end.date()

    count = 0
    while current <= end_date:
        date_dir = base_dir / current.isoformat()
        telemetry_path = date_dir / "telemetry.jsonl"
        if telemetry_path.exists():
            with telemetry_path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        payload = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    ts_raw = payload.get("timestamp")
                    if not isinstance(ts_raw, str):
                        continue
                    timestamp = _parse_timestamp(ts_raw)

                    if timestamp < start or timestamp > end:
                        continue

                    yield payload
                    count += 1
                    if limit is not None and count >= limit:
                        return
        current += timedelta(days=1)


def iter_last_n_days(base_dir: Path, days: int) -> Iterator[Dict[str, object]]:
    """Yield records for the last N days ending now."""

    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)
    yield from iter_telemetry_records(base_dir, start, end)
