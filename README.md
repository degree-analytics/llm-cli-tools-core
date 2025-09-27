# llm-cli-tools-core

Core telemetry and utilities for LLM CLI tools. Provides unified telemetry tracking, storage, and configuration for AI-powered command-line tools.

## Features

- 📊 **Unified Telemetry** - Track AI operations across all your tools
- 🔌 **Multi-Provider Support** - OpenRouter, Anthropic, OpenAI token extraction
- 💾 **Configurable Storage** - Each project owns its telemetry data
- 📈 **Prometheus Integration** - Push metrics to monitoring stack
- 🔄 **Session Tracking** - Automatic session correlation
- ⚡ **Zero Dependencies** - Minimal core dependencies

## Installation

### From GitHub Release (Recommended)
```bash
# Install specific version
uv pip install "llm-cli-tools-core @ git+https://github.com/spacecargo/llm-cli-tools-core@v0.1.0"

# Install latest from main branch
uv pip install "llm-cli-tools-core @ git+https://github.com/spacecargo/llm-cli-tools-core@main"
```

### For Development
```bash
git clone https://github.com/spacecargo/llm-cli-tools-core
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

## Configuration

Configure via `.env` file in your project root:

```bash
# Storage Configuration
LLM_TELEMETRY_DIR=.llm-telemetry        # Where to store telemetry data
LLM_TELEMETRY_ENABLED=true              # Enable/disable telemetry
LLM_PROMPT_STORAGE=true                 # Store prompts for analysis
LLM_RESPONSE_STORAGE=true               # Store responses for analysis

# Metrics Backend
LLM_METRICS_BACKEND=local               # local, pushgateway, or both
LLM_PUSHGATEWAY_URL=http://localhost:9101  # Prometheus pushgateway URL

# Session Detection (auto-detected in Claude Code)
CLAUDE_SESSION_ID=                      # Optional: Override session ID
CLAUDE_USER_ID=                          # Optional: Override user ID
```

## Development

### Setup Development Environment
```bash
# Clone the repository
git clone https://github.com/spacecargo/llm-cli-tools-core
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

### Running Tests
```bash
just test           # Run all tests
just test unit      # Run unit tests only
just test integration  # Run integration tests
```

## Architecture

```
llm-cli-tools-core/
├── telemetry/          # Core telemetry tracking
│   ├── core.py        # AITelemetryTracker, track_ai_call
│   ├── extractors.py  # Token extractors for different providers
│   └── session.py     # Session management
├── storage/            # Data storage backends
│   ├── local.py       # Local file storage
│   └── remote.py      # Remote storage options
├── providers/          # LLM provider wrappers
│   ├── anthropic.py   # Anthropic integration
│   ├── openrouter.py  # OpenRouter integration
│   └── openai.py      # OpenAI integration
└── config/             # Configuration management
    └── settings.py    # .env configuration loading
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
```
ai_agent_usage_total{agent_name="...", operation="...", model="..."}
ai_agent_tokens_total{agent_name="...", model="..."}
ai_agent_cost_usd_total{agent_name="...", model="..."}
ai_agent_duration_ms_total{agent_name="...", session_id="..."}
```

## License

MIT

## Support

For issues and questions:
- Open an issue on [GitHub](https://github.com/spacecargo/llm-cli-tools-core/issues)
- Check the [CLAUDE.md](CLAUDE.md) for development guidelines

## Roadmap

- [ ] Local storage implementation for prompts/responses
- [ ] Advanced configuration system
- [ ] Provider-specific wrappers with retry logic
- [ ] Cost calculation utilities
- [ ] Token counting before API calls
- [ ] Batch metrics sending
- [ ] Data mining and analysis tools