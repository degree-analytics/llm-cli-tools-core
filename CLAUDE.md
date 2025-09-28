---
purpose:
  "Set contributor expectations, tooling rules, and workflow guardrails for
  llm-cli-tools-core."
audience: "Contributors, reviewers, automation agents"
owner: "Core AI Tools"
review: "Quarterly (Jan, Apr, Jul, Oct)"
status: "Active"
---

# llm-cli-tools-core - Claude Development Guide

## 🎯 CORE PRINCIPLES

1. **UV-first development** - All Python operations through UV
2. **Justfile for everything** - Never run pytest, pip, or python directly
3. **Storage is configurable** - Each project owns its data via .env
4. **Test-driven development** - Write tests before implementation
5. **Git-based distribution** - No PyPI, use GitHub releases

## When to Use This

- Start here before making any change or opening a PR in llm-cli-tools-core.
- Reference during reviews to verify workflows, tooling, and testing
  requirements.

## Prerequisites

- Local environment bootstrapped with `just setup`.
- Access to required secrets for telemetry or GitHub releases when applicable.
- Node 18+ available locally to run `just docs check` (uses
  `npx markdownlint-cli2`).

## 🔧 DEVELOPMENT WORKFLOW

### Initial Setup

```bash
just setup       # Creates UV environment and installs dependencies
just test        # Verify everything works
```

### Making Changes

1. Create feature branch: `git checkout -b feat/your-feature`
2. Write tests first (TDD approach)
3. Implement feature
4. Run `just ci` to verify everything passes (and `just docs check` if
   documentation changed)
5. Commit with conventional message format:
   - `feat:` for new features (triggers minor version bump)
   - `fix:` for bug fixes (triggers patch version bump)
   - `chore:` for maintenance (no version bump)
   - Include `BREAKING CHANGE:` for major version bumps

### Testing

```bash
just test           # Run all tests
just test unit      # Run unit tests only
just test integration  # Run integration tests only
```

### Linting and Formatting

```bash
just lint check     # Check for lint issues
just lint format    # Auto-format code
```

## 📦 PACKAGE STRUCTURE

```text
src/llm_cli_core/
├── __init__.py           # Public API exports
├── telemetry/            # Telemetry tracking
│   ├── core.py          # Main telemetry logic
│   ├── extractors.py    # Token extractors (future)
│   └── session.py       # Session management (future)
├── storage/              # Data storage backends
├── providers/            # LLM provider wrappers
└── config/               # Configuration management
```

## 🧪 TESTING REQUIREMENTS

- **Unit tests** for all new functions
- **Integration tests** for storage operations
- **Mock external dependencies** (pushgateway, etc.)
- **Minimum 80% coverage** target
- **Use pytest fixtures** for common setup

## Verification

- Run `just ci` before requesting review to satisfy linting and test coverage
  expectations.
- Capture test output in PR descriptions for high-risk changes or failing
  investigations.
- `just docs check` now runs markdownlint, cspell, and lychee automatically via
  `scripts/docs_phase2.sh`; keep Node + Rust toolchain (lychee) available.

## 🚫 CRITICAL RULES

1. **NEVER hardcode paths** - Use .env configuration
2. **NEVER use pip directly** - Use `uv pip` if needed
3. **NEVER commit uv.lock** changes without testing
4. **NEVER manually change version** in pyproject.toml
5. **ALWAYS use justfile commands** for operations

## 📝 COMMIT MESSAGE CONVENTIONS

```text
feat: add new provider support
fix: correct token counting logic
chore: update dependencies
docs: improve API documentation
test: add integration tests
refactor: split telemetry module

BREAKING CHANGE: renamed main API function
```

## 🔄 VERSION MANAGEMENT

Versions are automatically managed by GitHub Actions based on commit messages:

- `feat:` → Minor bump (0.1.0 → 0.2.0)
- `fix:` → Patch bump (0.1.0 → 0.1.1)
- `BREAKING CHANGE:` → Major bump (0.1.0 → 1.0.0)

## 💾 STORAGE PHILOSOPHY

- Each project using this library owns its storage
- Storage location is configurable via `.env`
- Never assume storage paths
- Create directories if they don't exist
- Support multiple storage backends (local, remote)

## 🔌 INTEGRATION PATTERN

Projects using this library should:

1. Add to dependencies:

   ```text
   llm-cli-tools-core @ git+https://github.com/degree-analytics/llm-cli-tools-core@v0.1.0
   ```

2. Configure via `.env`:

   ```bash
   LLM_TELEMETRY_DIR=.llm-telemetry
   LLM_TELEMETRY_ENABLED=true
   ```

3. Import and use:

   ```python
   from llm_cli_core import track_ai_call, OpenRouterTokens

   with track_ai_call("my-agent", "operation") as tracker:
       response = make_api_call()
       tracker.record_tokens(OpenRouterTokens(response.json()))
   ```

## 🚀 FUTURE ENHANCEMENTS

Areas for expansion (not yet implemented):

- [ ] Local storage implementation
- [ ] Config loading from .env
- [ ] Provider wrappers (Anthropic, OpenAI)
- [ ] Token extractor separation
- [ ] Session management improvements
- [ ] Prompt/response storage
- [ ] Cost calculation utilities

## 🤝 HANDOFF NOTES

When handing off to another developer or LLM:

1. The core telemetry code is copied but not yet refactored
2. Tests are basic but functional
3. Storage and config modules are stubbed out
4. GitHub Actions are configured but not tested
5. Package can be installed locally but needs real-world testing

## 📚 KEY FILES

- `justfile` - All development commands
- `pyproject.toml` - Package configuration
- `src/llm_cli_core/telemetry/core.py` - Main telemetry logic (from
  ai_telemetry.py)
- `tests/unit/test_telemetry.py` - Basic telemetry tests
- `.github/workflows/` - CI/CD automation
