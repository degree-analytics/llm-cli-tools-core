---
purpose:
  "Capture product context, problem framing, and solution scope for
  llm-cli-tools-core."
audience: "Contributors, stakeholders, partner teams"
owner: "Core AI Tools"
review: "Quarterly (Jan, Apr, Jul, Oct)"
status: "Active"
---

# llm-cli-tools-core - Full Project Context

## When to Use This

- Onboard new collaborators who need the background behind llm-cli-tools-core.
- Explain strategic decisions to leadership or partner teams.

## Prerequisites

- Familiarity with the downstream repositories (Spacewalker, Mímir) that adopt
  the library.
- Access to telemetry metrics or issue tracker history when validating
  assumptions.

## 🎯 The Problem We're Solving

We have multiple AI-powered CLI tools across different repositories
(spacewalker, mimir, and more coming) that all need the same core functionality:

- Telemetry tracking for AI operations
- Token counting from different providers (OpenRouter, Anthropic, OpenAI)
- Cost tracking and metrics
- Session correlation
- Prometheus/Grafana integration

Currently, we have **identical copies** of `ai_telemetry.py` in:

- `/Users/chadwalters/source/work/spacewalker/scripts/helpers/ai_telemetry.py`
- `/Users/chadwalters/source/work/mimir/src/mimir/core/ai_telemetry.py`

This duplication is problematic because:

1. Bug fixes need to be applied in multiple places
2. Enhancements aren't shared across projects
3. Each project might diverge over time
4. No centralized place to add new features

## 🚀 The Solution: llm-cli-tools-core

A shared library that provides:

1. **Unified telemetry** for all LLM operations
2. **Configurable storage** - each project owns its data
3. **Provider abstraction** - support for OpenRouter, Anthropic, OpenAI, etc.
4. **Future expansion** - prompt storage, response mining, cost optimization

## 📊 What We Built Today

### Repository Structure

```text
llm-cli-tools-core/
├── src/llm_cli_core/
│   ├── telemetry/core.py     # The ai_telemetry.py code (copied, not refactored)
│   ├── storage/              # Placeholder for storage implementations
│   ├── providers/            # Placeholder for provider wrappers
│   └── config/               # Placeholder for configuration
├── tests/unit/               # Basic tests (70% passing)
├── .github/workflows/        # CI/CD and auto-versioning
├── justfile                  # UV-based development workflow
├── CLAUDE.md                 # Development guidelines
└── README.md                 # User documentation
```

### Key Design Decisions

1. **UV-First Development**
   - Using UV instead of pip for speed and reliability
   - All operations through justfile commands
   - No direct pip/pytest/python commands

2. **GitHub as Package Registry**
   - No PyPI account needed
   - Install via:
     `uv pip install "llm-cli-tools-core @ git+https://github.com/spacecargo/llm-cli-tools-core@v0.1.0"`
   - Automatic versioning based on commit messages

3. **Per-Project Storage**
   - Each project stores its own telemetry data
   - Configured via `.env` file
   - Example: spacewalker stores in `spacewalker/.llm-telemetry/`

4. **Backward Compatibility**
   - All existing code using `ai_telemetry.py` will work unchanged
   - Just change the import from local file to package

## 🎯 Current State

### What Works ✅

- Package structure is created and valid
- Telemetry code is copied and imports work
- Can be installed via git: `uv pip install -e ~/source/work/llm-cli-tools-core`
- Basic functionality tested and working
- GitHub Actions configured for CI/CD
- Auto-versioning based on commit messages

### What Needs Completion 🔧

#### 1. **Fix Failing Tests** (Priority: HIGH)

- 3 tests fail due to mock path issues
- The `requests` module is imported inside functions, not at module level
- Need to fix mock patches to use the correct import path

#### 2. **Refactor Monolithic File** (Priority: MEDIUM)

Currently `telemetry/core.py` has everything. Should be split:

```python
# telemetry/extractors.py
class OpenRouterTokens: ...
class AnthropicTokens: ...
class OpenAITokens: ...

# telemetry/session.py
class SessionInfo: ...

# telemetry/core.py (keep)
class AITelemetryTracker: ...
def track_ai_call(): ...
```

#### 3. **Implement Storage Layer** (Priority: HIGH)

```python
# storage/local.py
class LocalStorage:
    def store_prompt(self, prompt, metadata): ...
    def store_response(self, response, metadata): ...
    def list_prompts(self, filters): ...

# storage/base.py
class StorageBackend(ABC): ...
```

#### 4. **Add Configuration System** (Priority: HIGH)

```python
# config/settings.py
class Config:
    def __init__(self):
        load_dotenv()
        self.telemetry_dir = os.getenv('LLM_TELEMETRY_DIR', '.llm-telemetry')
        self.telemetry_enabled = os.getenv('LLM_TELEMETRY_ENABLED', 'true')
        # ... etc
```

Install via:

```bash
uv pip install "llm-cli-tools-core @ git+https://github.com/degree-analytics/llm-cli-tools-core@v0.1.0"
```

#### 5. **Integration Testing** (Priority: MEDIUM)

- Test with real projects (spacewalker, mimir)
- Ensure backward compatibility
- Verify storage isolation

## Verification

- Confirm this document reflects the latest architecture decisions during the
  scheduled quarterly review.
- Cross-check downstream repositories (Spacewalker, Mímir) after major releases
  to ensure assumptions remain accurate.

## 🎯 Success Criteria

The v0.1.0 release is ready when:

1. **All tests pass**: `just test` returns success
2. **Clean linting**: `just lint check` has no errors
3. **Imports work**: Can import in other projects without changes
4. **Storage works**: Telemetry data saves to configured location
5. **Backward compatible**: Existing code needs only import change

## 🔮 Future Vision (Not for v0.1.0)

After the initial release, we want to add:

1. **Enhanced Telemetry**
   - Store all prompts and responses for analysis
   - Track quality metrics
   - Pattern recognition

2. **Provider Wrappers**

   ```python
   from llm_cli_core.providers import AnthropicProvider

   provider = AnthropicProvider(auto_telemetry=True)
   response = provider.complete(prompt)  # Telemetry automatic
   ```

3. **Cost Optimization**
   - Automatic model selection based on task
   - Cost budgeting and alerts
   - Token counting before API calls

4. **Rate Limiting & Retry**
   - Intelligent backoff
   - Provider-specific rate limits
   - Automatic failover

5. **Mining & Analysis**
   - Find successful prompt patterns
   - Identify failure modes
   - Build prompt libraries

## 📋 Immediate Next Steps

1. **Fix the 3 failing tests** - Mock path issues
2. **Test in a real project** - Try replacing ai_telemetry.py in spacewalker
3. **Split the monolithic file** - Better code organization
4. **Add storage implementation** - Start with local JSON files
5. **Add config loading** - Read from .env files

## 🤔 Questions to Consider

When you read this, consider:

1. **Storage Format**: Should we use JSON, SQLite, or something else for local
   storage?
2. **Naming**: Is `llm-cli-tools-core` the best name, or should it be simpler?
3. **Scope**: Should v0.1.0 include storage, or just fix the telemetry?
4. **Testing**: What level of test coverage is acceptable for v0.1.0?
5. **Migration**: Should we provide a migration script for existing projects?

## 📂 Related Files to Review

- `justfile` - See all available commands
- `CLAUDE.md` - Development guidelines and rules
- `src/llm_cli_core/telemetry/core.py` - The main code (needs refactoring)
- `tests/unit/test_telemetry.py` - Tests that need fixing
- `.github/workflows/` - CI/CD setup

## 🎯 The Ask

Please:

1. Read this context and the CLAUDE.md file
2. Ask any clarifying questions you have
3. Fix the failing tests first (mock path issues)
4. Then proceed with refactoring and enhancements
5. Keep changes minimal for v0.1.0 - we can add features later

The goal is a **working, installable package** that eliminates code duplication
across our projects. Everything else can be added incrementally.

## 💡 Why This Matters

We're building more AI tools all the time. Having a solid foundation for
telemetry, storage, and configuration means:

- Consistent metrics across all tools
- Better understanding of AI usage and costs
- Ability to mine prompts and improve quality
- Faster development of new tools
- Single place to fix bugs and add features

This is infrastructure that will pay dividends as we scale our AI tooling
ecosystem.
