# llm-cli-tools-core developer commands
set dotenv-load
set shell := ["bash", "-c"]

# Use UV for all Python operations
python := "uv run python"
pytest := "uv run pytest"
ruff := "uv run ruff"

_default:
    @just help

# Show available commands
help:
    @echo "llm-cli-tools-core - Justfile Commands"
    @echo "======================================"
    @echo "Setup:"
    @echo "  just setup                 - Initialize development environment"
    @echo ""
    @echo "Development:"
    @echo "  just test [target]         - Run tests (all/unit/integration)"
    @echo "  just lint [action]         - Lint code (check/format)"
    @echo "  just ci                    - Run full CI pipeline"
    @echo ""
    @echo "Installation:"
    @echo "  just install-local         - Install package locally for testing"

# Initialize development environment
setup:
    @echo "🔧 Setting up development environment..."
    @uv venv
    @uv sync --all-extras
    @echo "✅ Development environment ready"

# Run tests
test target='all':
    @if [ "{{target}}" = "all" ]; then \
        {{pytest}} tests/ -v --cov=src/llm_cli_core --cov-report=term-missing; \
    elif [ "{{target}}" = "unit" ]; then \
        {{pytest}} tests/unit -v; \
    elif [ "{{target}}" = "integration" ]; then \
        {{pytest}} tests/integration -v; \
    else \
        echo "Unknown test target: {{target}}"; \
        exit 1; \
    fi

# Lint and format code
lint action='check':
    @if [ "{{action}}" = "check" ]; then \
        {{ruff}} check src/ tests/; \
    elif [ "{{action}}" = "format" ]; then \
        {{ruff}} format src/ tests/; \
        {{ruff}} check --fix src/ tests/; \
    else \
        echo "Unknown lint action: {{action}}"; \
        exit 1; \
    fi

# Run CI pipeline
ci:
    @echo "🚀 Running CI pipeline..."
    @just lint check
    @just test all
    @echo "✅ CI pipeline passed"

# Install package locally for testing
install-local:
    @echo "📦 Installing package locally..."
    @uv pip install -e .
    @echo "✅ Package installed"