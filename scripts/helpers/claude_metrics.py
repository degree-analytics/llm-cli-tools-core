from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Iterable, Iterator, Mapping, Sequence

Number = int | float


@dataclass(frozen=True)
class Metrics:
    in_tokens: int
    out_tokens: int
    model: str
    est_cost_usd: Decimal | None = None

    def to_output_pairs(self) -> Iterator[tuple[str, str]]:
        yield "in_tokens", str(self.in_tokens)
        yield "out_tokens", str(self.out_tokens)
        if self.model:
            yield "model", self.model
        if self.est_cost_usd is not None:
            yield "est_cost_usd", f"{self.est_cost_usd:.6f}"


INPUT_PATHS: Sequence[Sequence[str]] = (
    ("usage", "inputTokens"),
    ("usage", "input_tokens"),
    ("metrics", "input_tokens"),
    ("result", "usage", "input_tokens"),
    ("result", "usage", "inputTokens"),
)
OUTPUT_PATHS: Sequence[Sequence[str]] = (
    ("usage", "outputTokens"),
    ("usage", "output_tokens"),
    ("metrics", "output_tokens"),
    ("result", "usage", "output_tokens"),
    ("result", "usage", "outputTokens"),
)
MODEL_PATHS: Sequence[Sequence[str]] = (
    ("model",),
    ("meta", "model"),
    ("result", "model"),
)


class MetricsParseError(ValueError):
    """Raised when the execution metrics payload is malformed."""


def collect_metrics_from_file(
    execution_path: Path | str,
    *,
    costs_json: str | None = None,
    costs_file: Path | str | None = None,
    fallback_in_rate: Decimal | Number | str | None = None,
    fallback_out_rate: Decimal | Number | str | None = None,
) -> Mapping[str, object]:
    path = Path(execution_path)
    records = _load_records(path)
    in_tokens = _sum_fields(records, INPUT_PATHS)
    out_tokens = _sum_fields(records, OUTPUT_PATHS)
    model = _pick_model(records)
    cost_map = _load_cost_map(costs_json, costs_file)
    rates = _resolve_rates(model, cost_map, fallback_in_rate, fallback_out_rate)
    est_cost = _estimate_cost(in_tokens, out_tokens, rates)
    if est_cost is not None:
        est_cost = est_cost.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
    metrics = Metrics(in_tokens=in_tokens, out_tokens=out_tokens, model=model, est_cost_usd=est_cost)
    output: dict[str, object] = {
        "in_tokens": metrics.in_tokens,
        "out_tokens": metrics.out_tokens,
    }
    if metrics.model:
        output["model"] = metrics.model
    if metrics.est_cost_usd is not None:
        output["est_cost_usd"] = metrics.est_cost_usd
    return output


def _load_records(path: Path) -> list[dict]:
    try:
        raw = path.read_text().strip()
    except FileNotFoundError as exc:
        raise MetricsParseError(f"Execution file not found: {path}") from exc
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        records: list[dict] = []
        for line in raw.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:  # pragma: no cover
                raise MetricsParseError(f"Invalid JSON line in {path!s}") from exc
        if not records:
            raise MetricsParseError(f"Execution file {path!s} does not contain valid JSON")
        return records
    if isinstance(parsed, list):
        return [item for item in parsed if isinstance(item, dict)]
    if isinstance(parsed, dict):
        return [parsed]
    raise MetricsParseError(f"Unexpected payload type in {path!s}: {type(parsed).__name__}")


def _sum_fields(records: Iterable[Mapping[str, object]], paths: Sequence[Sequence[str]]) -> int:
    total = 0
    for record in records:
        for path in paths:
            value = _dig(record, path)
            if isinstance(value, (int, float)):
                total += int(value)
                break
    return total


def _pick_model(records: Iterable[Mapping[str, object]]) -> str:
    model_candidates: list[str] = []
    for record in records:
        for path in MODEL_PATHS:
            value = _dig(record, path)
            if isinstance(value, str):
                model_candidates.append(value)
    return model_candidates[-1] if model_candidates else "unknown"


def _dig(record: Mapping[str, object], path: Sequence[str]) -> object | None:
    current: object | None = record
    for key in path:
        if not isinstance(current, Mapping):
            return None
        current = current.get(key)
    return current


def _load_cost_map(costs_json: str | None, costs_file: Path | str | None) -> dict[str, dict[str, Number]] | None:
    if costs_json:
        try:
            return json.loads(costs_json)
        except json.JSONDecodeError as exc:
            raise MetricsParseError("Invalid COSTS_JSON payload") from exc
    if costs_file:
        file_path = Path(costs_file)
        if file_path.is_file():
            try:
                with file_path.open("r", encoding="utf-8") as fh:
                    return json.load(fh)
            except json.JSONDecodeError as exc:  # pragma: no cover
                raise MetricsParseError(f"Invalid JSON in costs file: {costs_file}") from exc
    return None


def _resolve_rates(
    model: str,
    cost_map: Mapping[str, Mapping[str, Number]] | None,
    fallback_in_rate: Decimal | Number | str | None,
    fallback_out_rate: Decimal | Number | str | None,
) -> tuple[Decimal | None, Decimal | None]:
    if cost_map and model in cost_map:
        entry = cost_map[model]
        return _coerce_decimal(entry.get("in")), _coerce_decimal(entry.get("out"))
    return _coerce_decimal(fallback_in_rate), _coerce_decimal(fallback_out_rate)


def _coerce_decimal(value: Decimal | Number | str | None) -> Decimal | None:
    if value in (None, ""):
        return None
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except Exception as exc:  # pragma: no cover
        raise MetricsParseError(f"Unable to coerce value '{value}' to Decimal") from exc


def _estimate_cost(
    in_tokens: int,
    out_tokens: int,
    rates: tuple[Decimal | None, Decimal | None],
) -> Decimal | None:
    in_rate, out_rate = rates
    if in_rate is None or out_rate is None:
        return None
    million = Decimal("1000000")
    cost_in = (Decimal(in_tokens) / million) * in_rate
    cost_out = (Decimal(out_tokens) / million) * out_rate
    return cost_in + cost_out


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Aggregate Claude execution metrics")
    parser.add_argument("execution_file", type=Path)
    parser.add_argument("--costs-json", dest="costs_json")
    parser.add_argument("--costs-file", dest="costs_file")
    parser.add_argument("--fallback-in-rate", dest="fallback_in_rate")
    parser.add_argument("--fallback-out-rate", dest="fallback_out_rate")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    metrics = collect_metrics_from_file(
        args.execution_file,
        costs_json=args.costs_json,
        costs_file=args.costs_file,
        fallback_in_rate=args.fallback_in_rate,
        fallback_out_rate=args.fallback_out_rate,
    )
    for key, value in metrics.items():
        print(f"{key}={value}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
