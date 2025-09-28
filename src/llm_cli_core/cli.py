"""Command line interface for llm-cli-tools-core."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, Optional

from rich.console import Console
from rich.table import Table

from llm_cli_core.analytics import CostFilters, build_cost_report
from llm_cli_core.config import get_config
from llm_cli_core.models.pricing import get_pricing_cache

console = Console()


def main(argv: Optional[list[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "costs":  # type: ignore[attr-defined]
        return _handle_costs(args)

    parser.print_help()
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="llm-telemetry", description="Telemetry analytics for LLM CLI tools"
    )
    subparsers = parser.add_subparsers(dest="command")

    costs = subparsers.add_parser("costs", help="Show token spend over time")
    costs.add_argument("--path", type=str, help="Telemetry directory (defaults to config)")
    costs.add_argument("--days", type=int, default=30, help="Number of days to include")
    costs.add_argument("--project", type=str, help="Filter by project name")
    costs.add_argument("--agent", type=str, help="Filter by agent name")
    costs.add_argument("--model", type=str, help="Filter by model name")
    costs.add_argument(
        "--status",
        type=str,
        choices=["success", "failure"],
        help="Filter by success or failure",
    )
    costs.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Output JSON instead of rich table",
    )

    return parser


def _handle_costs(args: argparse.Namespace) -> int:
    config = get_config()
    base_dir = Path(args.path).expanduser().resolve() if args.path else config.resolve_telemetry_dir()

    if not base_dir.exists():
        console.print(f"[red]Telemetry directory not found:[/] {base_dir}")
        return 1

    filters = CostFilters(
        project=args.project,
        agent=args.agent,
        model=args.model,
        status=args.status,
    )

    pricing = get_pricing_cache()
    report = build_cost_report(
        base_dir,
        days=max(args.days, 1),
        pricing=pricing,
        filters=filters,
    )

    if args.as_json:
        console.print_json(data=report)
        return 0

    return _render_cost_report(report)


def _render_cost_report(report: Dict[str, Any]) -> int:
    total_calls = report.get("total_calls", 0)
    if total_calls == 0:
        console.print("[yellow]No telemetry records found for the selected window.[/]")
        return 0

    total_cost = report.get("total_cost", 0.0)
    tokens = report.get("total_tokens", {})
    window = report.get("window", {})
    filters = report.get("filters", {})

    console.print("[bold cyan]Telemetry Cost Report[/bold cyan]")
    console.print(
        f"Window: {window.get('start', 'unknown')} → {window.get('end', 'unknown')}"
        f" (last {window.get('days', '?')} days)"
    )

    if filters:
        rendered_filters = ", ".join(f"{k}={v}" for k, v in filters.items())
        console.print(f"Filters: {rendered_filters}")

    console.print(f"Total calls: {total_calls}")
    console.print(f"Total cost: {format_currency(total_cost)}")
    console.print(
        "Tokens: input {input:,} | output {output:,} | total {total:,}".format(
            input=tokens.get("input", 0),
            output=tokens.get("output", 0),
            total=tokens.get("total", 0),
        )
    )

    console.print()
    console.print("[bold]Cost by model[/bold]")
    console.print(_build_cost_table(report.get("by_model", {})))

    console.print()
    console.print("[bold]Cost by agent[/bold]")
    console.print(_build_cost_table(report.get("by_agent", {})))

    return 0


def _build_cost_table(section: Dict[str, Dict[str, Any]]) -> Table:
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Name", justify="left")
    table.add_column("Calls", justify="right")
    table.add_column("Cost (USD)", justify="right")
    table.add_column("Tokens", justify="right")

    if not section:
        table.add_row("(none)", "0", "$0.00", "0")
        return table

    for name, stats in section.items():
        tokens = stats.get("tokens", {})
        table.add_row(
            name,
            f"{stats.get('calls', 0):,}",
            format_currency(stats.get("cost_usd", 0.0)),
            f"{tokens.get('total', 0):,}",
        )
    return table


def format_currency(value: Any) -> str:
    try:
        amount = float(value)
    except (TypeError, ValueError):
        return "$0.00"
    return f"${amount:,.4f}"


if __name__ == "__main__":
    raise SystemExit(main())
