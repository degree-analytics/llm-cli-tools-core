---
purpose:
  "Document llm-cli-tools-core capabilities, installation, and quick start
  usage."
audience: "Developers, integrators, and maintainers"
owner: "Core AI Tools"
review: "Quarterly (Jan, Apr, Jul, Oct)"
status: "Active"
---

# llm-cli-tools-core

Core telemetry and utilities for LLM CLI tools. Provides unified telemetry
tracking, storage, and configuration for AI-powered command-line tools.

## When to Use This

- Consolidate telemetry, cost, and token accounting across AI-driven CLIs.
- Share a single instrumentation library between repositories such as
  Spacewalker and Mímir.

## Prerequisites

- Python 3.11 or newer with [`uv`](https://docs.astral.sh/uv/) installed.
- Read access to the GitHub repository releases (or main branch) when
  installing.

## Features

- 📊 **Unified Telemetry** - Track AI operations across all your tools
- 🔌 **Multi-Provider Support** - OpenRouter, Anthropic, OpenAI token extraction
- 💾 **Configurable Storage** - Each project owns its telemetry data
- 📈 **Prometheus Integration** - Push metrics to monitoring stack
- 🔄 **Session Tracking** - Automatic session correlation
- 💰 **Cost Analytics CLI** - Summarize spend with `llm-telemetry costs`
- ⚡ **Lightweight Footprint** - Minimal runtime dependencies

## Installation

### From GitHub Release (Recommended)

```bash
# Install specific version
uv pip install "llm-cli-tools-core @ git+https://github.com/degree-analytics/llm-cli-tools-core@v0.1.0"

# Install latest from main branch
uv pip install "llm-cli-tools-core @ git+https://github.com/degree-analytics/llm-cli-tools-core@main"
```

### For Development

```bash
git clone https://github.com/degree-analytics/llm-cli-tools-core
cd llm-cli-tools-core
just setup          # Set up development environment
just test           # Run tests
just install-local  # Install in editable mode
```

## Quick Start

### Basic Usage

```python
from llm_cli_core import track_ai_call, OpenRouterTokens

# Track an AI operation
with track_ai_call("my-agent", "document-search") as tracker:
    # Make your API call
    response = openrouter_client.post(...)

    # Record metrics
    tracker.record_tokens(OpenRouterTokens(response.json()))
    tracker.record_cost(0.003)
    tracker.record_model("gpt-4")
```

### Different Provider Support

```python
# OpenRouter
from llm_cli_core import OpenRouterTokens
tracker.record_tokens(OpenRouterTokens(response_json))

# Anthropic
from llm_cli_core import AnthropicTokens
tracker.record_tokens(AnthropicTokens(anthropic_response))

# OpenAI
from llm_cli_core import OpenAITokens
tracker.record_tokens(OpenAITokens(openai_response_json))
```

### Legacy Compatibility

```python
from llm_cli_core import send_agent_metrics

# For older code that uses the legacy function
send_agent_metrics(
    agent_name="my-agent",
    operation="search",
    duration_ms=1500,
    token_count=100,
    cost_usd=0.002
)
```

## Verification

- Run `just test` before publishing changes to confirm the telemetry suite
  passes.
- Execute the quick start example against a sandbox provider and confirm metrics
  are recorded as expected.

## Configuration

Configure via `.env` file in your project root:

```bash
# Storage Configuration
LLM_TELEMETRY_ENABLED=true                 # Enable/disable telemetry entirely
LLM_TELEMETRY_STORAGE_ENABLED=true         # Toggle local storage writes
LLM_TELEMETRY_DIR=.llm-telemetry           # Where to store telemetry JSONL files
LLM_PROJECT_NAME=spacewalker               # Optional explicit project label

# Optional payload storage
LLM_STORE_PROMPTS=false                    # Persist full prompts (default: off)
LLM_STORE_RESPONSES=false                  # Persist full responses (default: off)

# Metrics Backend
LLM_PUSHGATEWAY_URL=http://localhost:7101  # Prometheus pushgateway URL

# Session Detection (auto-detected in Claude Code)
CLAUDE_SESSION_ID=                      # Optional: Override session ID
CLAUDE_USER_ID=                          # Optional: Override user ID
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/degree-analytics/llm-cli-tools-core
cd llm-cli-tools-core

# Set up UV environment
just setup

# Run tests
just test

# Lint and format
just lint format
just lint check

# Run full CI pipeline
just ci
```

### GitHub App Access For CI

Org repositories that need read access to `llm-cli-tools-core` via GitHub
Actions should follow the shared GitHub App setup described in
`docs/development/github-app-integration.md`.

### Running Tests

```bash
just test           # Run all tests
just test unit      # Run unit tests only
just test integration  # Run integration tests
```

## Telemetry Storage

Telemetry is stored as newline-delimited JSON in the configured directory
(default: `.llm-telemetry/`).

```text
.llm-telemetry/
├── 2025-01-27/
│   └── telemetry.jsonl       # One record per AI call
├── 2025-01-28/
│   └── telemetry.jsonl
└── summary.json              # Rolling totals (cost, tokens, per-agent/model)
```

Prompts/responses are written to `prompts.jsonl` and `responses.jsonl` only when
explicitly enabled via `LLM_STORE_PROMPTS` / `LLM_STORE_RESPONSES`.

## CLI Analytics

A first analytics command ships in v0.2.0:

```bash
# Human-friendly table (last 30 days by default)
llm-telemetry costs

# JSON output for scripts / dashboards
llm-telemetry costs --json

# Filter by project, agent, status, or model
llm-telemetry costs --project spacewalker --agent doc-finder \
  --status success --days 7
```

Output includes total cost, total tokens, and breakdowns by model and agent.
Pricing data is cached locally and refreshed automatically (at most once every 7
days).

## GitHub Automation

This repository ships the same Claude and Codex review automation used in our
other projects:

- `.github/workflows/claude.yml` – trigger with `@claude` or `/claude` comments
  to request targeted AI reviews (docs, correctness, overengineering, justfile).
  Requires Anthropic API credentials (`ANTHROPIC_API_KEY`, optional secrets
  described in the workflow) and supports manual `workflow_dispatch` runs.
- `.github/workflows/codex-review.yml` – trigger with `@codex` or `/codex`
  comments for GPT-based reviews. Requires `OPENAI_API_KEY` and posts sticky
  summaries plus inline comments.

Both workflows rely on repository/organization variables (e.g.
`CLAUDE_MAX_TURNS`) and secrets mirroring the Spacewalker setup. Copy those
values into this repo before enabling the automations.

For day-to-day usage tips and GT/Claude best practices, see:

- `docs/claude-components/deployment-gt-workflow.md` – required GT branching
  workflow
- `docs/development/claude-commands.md` – available slash commands (including
  Ground Truth)
- `docs/workflows/claude-review-workflows.md` – how multi-focus reviews operate

## Architecture

```text
llm-cli-tools-core/
├── analytics/              # Aggregations used by the CLI
│   └── costs.py
├── cli.py                  # `llm-telemetry` entry point
├── config/settings.py      # Environment / .env configuration
├── models/pricing.py       # Pricing cache + estimation helpers
├── storage/
│   ├── base.py             # Storage interface + record dataclass
│   ├── local.py            # JSONL storage backend
│   └── readers.py          # Iterators for analytics
└── telemetry/core.py       # Tracker, context manager, and extractors
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/amazing-feature`)
3. Write tests for your changes
4. Ensure tests pass (`just ci`)
5. Commit with conventional commit message (`feat: add amazing feature`)
6. Push to your fork and create a Pull Request

### Commit Message Format

- `feat:` - New features (triggers minor version bump)
- `fix:` - Bug fixes (triggers patch version bump)
- `chore:` - Maintenance tasks (no version bump)
- `docs:` - Documentation updates (no version bump)
- `BREAKING CHANGE:` - Breaking changes (triggers major version bump)

## Metrics Captured

- **Token Usage**: Input, output, and total tokens
- **Cost Tracking**: USD cost per operation
- **Model Information**: Which AI model was used
- **Operation Timing**: Duration of each operation
- **Session Correlation**: User and session tracking
- **Success/Failure**: Operation success status

## Integration with Monitoring

The library integrates with Prometheus/Grafana through pushgateway:

```python
# Metrics are automatically pushed if configured
# Set LLM_PUSHGATEWAY_URL in your .env file
LLM_PUSHGATEWAY_URL=http://localhost:9101
```

Metrics format:

```text
ai_agent_usage_total{agent_name="...", operation="...", model="..."}
ai_agent_tokens_total{agent_name="...", model="..."}
ai_agent_cost_usd_total{agent_name="...", model="..."}
ai_agent_duration_ms_total{agent_name="...", session_id="..."}
```

## License

MIT

## Support

For issues and questions:

- Open an issue on
  [GitHub](https://github.com/degree-analytics/llm-cli-tools-core/issues)
- Check the [CLAUDE.md](CLAUDE.md) for development guidelines

## Roadmap

- [ ] Local storage implementation for prompts/responses
- [ ] Advanced configuration system
- [ ] Provider-specific wrappers with retry logic
- [ ] Cost calculation utilities
- [ ] Token counting before API calls
- [ ] Batch metrics sending
- [ ] Data mining and analysis tools
