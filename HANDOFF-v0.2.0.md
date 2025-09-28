# 🎯 HANDOFF: Implement v0.2.0 - Storage + Client Abstractions

## Your Mission
Transform llm-cli-tools-core from just telemetry tracking into a complete LLM toolkit:
1. **Add local storage** - Save telemetry to disk for analysis
2. **Create client abstractions** - Unified interface for all LLM providers
3. **Build model registry** - Centralized model configurations
4. **Extract common utilities** - Token estimation, retry logic, etc.

## Current State (v0.1.0)
- ✅ Telemetry tracking works (AITelemetryTracker class)
- ✅ Sends metrics to Prometheus pushgateway
- ❌ No local storage - data is ephemeral
- ❌ No way to analyze historical data

## What You Need to Build

### 1. Create Storage Module
**File**: `src/llm_cli_core/storage/__init__.py`
```python
from .local import LocalStorage
__all__ = ["LocalStorage"]
```

**File**: `src/llm_cli_core/storage/local.py`
```python
import json
import os
from pathlib import Path
from datetime import datetime, UTC
from typing import Dict, Any, List, Optional
import threading
import hashlib

class LocalStorage:
    """Thread-safe local JSON Lines storage for telemetry data"""

    def __init__(self, base_dir: Optional[Path] = None):
        # Get directory from env or use default
        if base_dir is None:
            base_dir = os.getenv("LLM_TELEMETRY_DIR", ".llm-telemetry")
        self.base_dir = Path(base_dir)
        self._lock = threading.Lock()

    def store_telemetry(self, data: Dict[str, Any]) -> bool:
        """Store telemetry record in today's JSONL file"""
        # Implementation:
        # 1. Create directory structure: base_dir/YYYY-MM-DD/
        # 2. Append to telemetry.jsonl atomically
        # 3. Optionally store prompts.jsonl and responses.jsonl
        # 4. Update summary.json with rolling stats
        # 5. Clean old data if over retention period

    def query_by_date_range(self, start_date, end_date) -> List[Dict]:
        """Query telemetry records by date range"""
        # Read JSONL files from date directories

    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics"""
        # Read summary.json or calculate from recent data
```

### 2. Integrate with Existing Tracker
**Modify**: `src/llm_cli_core/telemetry/core.py`

In the `AITelemetryTracker.send_metrics()` method, after sending to Prometheus:

```python
def send_metrics(self):
    # ... existing Prometheus code ...

    # NEW: Store locally if enabled
    if os.getenv("LLM_TELEMETRY_STORAGE", "true").lower() == "true":
        from ..storage import LocalStorage
        storage = LocalStorage()

        telemetry_data = {
            "timestamp": datetime.now(UTC).isoformat(),
            "agent_name": self.agent_name,
            "operation": self.operation,
            "model": self.model,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "duration_ms": int((self.end_time - self.start_time) * 1000),
            "tokens": {
                "input": self.tokens.input,
                "output": self.tokens.output,
                "total": self.tokens.total,
            },
            "cost_usd": self.cost,
            "success": self.success,
            "project": Path.cwd().name,  # Auto-detect project
        }

        # Store prompts/responses if configured
        if hasattr(self, 'prompt') and os.getenv("LLM_STORE_PROMPTS", "false").lower() == "true":
            telemetry_data["prompt"] = self.prompt
            telemetry_data["prompt_hash"] = hashlib.sha256(self.prompt.encode()).hexdigest()

        if hasattr(self, 'response') and os.getenv("LLM_STORE_RESPONSES", "false").lower() == "true":
            telemetry_data["response"] = self.response
            telemetry_data["response_hash"] = hashlib.sha256(self.response.encode()).hexdigest()

        storage.store_telemetry(telemetry_data)
```

### 3. Create LLM Client Abstractions
**File**: `src/llm_cli_core/clients/base.py`
```python
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class LLMResponse:
    content: str
    model: str
    tokens: Dict[str, int]
    cost: float
    cached: bool = False

class BaseLLMClient(ABC):
    @abstractmethod
    def chat(self, prompt: str, system: Optional[str] = None, **kwargs) -> LLMResponse:
        pass
```

**File**: `src/llm_cli_core/clients/anthropic_client.py`
```python
# Port existing AIClient from spacewalker/scripts/helpers/ai_client.py
# Key features to preserve:
# - Model selection (haiku, sonnet, opus)
# - Prompt caching
# - Token estimation
# - Error handling
```

**File**: `src/llm_cli_core/clients/openrouter_client.py`
```python
# Port existing OpenRouterClient from spacewalker/scripts/doc-finder/
# Key features to preserve:
# - Model selection
# - API key handling
# - Response parsing
```

### 4. Create Model Registry
**File**: `src/llm_cli_core/models/registry.py`
```python
# Port MODEL_CAPABILITIES and MODEL_PRICING from ai_client.py
MODEL_REGISTRY = {
    "claude-3-5-haiku-20241022": {
        "provider": "anthropic",
        "context_window": 200000,
        "max_output": 8192,
        "pricing": {"input": 0.25, "output": 1.25},
        "capabilities": ["vision", "function_calling"],
        "aliases": ["haiku", "claude-haiku"]
    },
    # ... more models
}
```

### 5. Extract Common Utilities
**File**: `src/llm_cli_core/utils/tokens.py`
```python
def estimate_tokens(text: str, model: str = None) -> int:
    """Port _estimate_tokens from ai_client.py"""
    # Rough estimation: ~4 characters per token
    return len(text) // 4
```

**File**: `src/llm_cli_core/utils/retry.py`
```python
# Generic retry logic with exponential backoff
# Extract from various retry implementations
```

### 6. Create CLI Query Tool
**File**: `src/llm_cli_core/cli.py`
```python
#!/usr/bin/env python3
"""CLI for querying telemetry data"""

import click
from datetime import datetime, timedelta
from .storage import LocalStorage

@click.group()
def cli():
    """LLM telemetry query tool"""
    pass

@cli.command()
@click.option('--days', default=1, help='Number of days to show')
def stats(days):
    """Show usage statistics"""
    storage = LocalStorage()
    # Show costs, token usage, model distribution

@cli.command()
def costs():
    """Show cost breakdown"""
    storage = LocalStorage()
    # Show costs by model, agent, time period

if __name__ == "__main__":
    cli()
```

### 4. Update Configuration
**File**: `.env.example` (already exists, needs update)
```bash
# Storage Configuration
LLM_TELEMETRY_STORAGE=true          # Enable local storage
LLM_TELEMETRY_DIR=.llm-telemetry    # Where to store telemetry data
LLM_STORE_PROMPTS=false             # Store full prompts (privacy concern)
LLM_STORE_RESPONSES=false           # Store full responses (storage concern)
LLM_RETENTION_DAYS=30               # Keep data for N days
LLM_STORAGE_MAX_SIZE_MB=100        # Max storage size
```

### 5. Add Tests
**File**: `tests/unit/test_storage.py`
```python
def test_local_storage_creates_directories():
    """Test that storage creates date-based directories"""

def test_concurrent_writes():
    """Test thread-safe concurrent writes"""

def test_retention_cleanup():
    """Test old data is cleaned up"""

def test_query_by_date_range():
    """Test querying data by date range"""
```

## Implementation Steps

### Week 1: Foundation
1. **Storage Module** (Day 1)
   - Create LocalStorage class with JSONL backend
   - Implement thread-safe writes
   - Add retention and cleanup logic

2. **Client Abstractions** (Day 2)
   - Create BaseLLMClient interface
   - Port AnthropicClient from ai_client.py
   - Port OpenRouterClient from doc-finder
   - Implement client factory with auto-detection

3. **Model Registry** (Day 3)
   - Port MODEL_CAPABILITIES from ai_client.py
   - Create comprehensive model database
   - Add model selection logic

### Week 2: Integration
4. **Common Utilities** (Day 4)
   - Extract token estimation logic
   - Create retry decorator
   - Implement prompt caching utilities

5. **Integration & Testing** (Day 5)
   - Update telemetry to use new storage
   - Integrate clients with telemetry
   - Write comprehensive tests
   - Update documentation

6. **CLI & Polish** (Day 6)
   - Create CLI query tools
   - Test with real projects
   - Performance optimization
   - Release preparation

## Testing Plan

```bash
# After implementation:
cd /Users/chadwalters/source/work/llm-cli-tools-core

# Run tests
just test

# Test with spacewalker
cd ../spacewalker
python -c "from llm_cli_core import track_ai_call
with track_ai_call('test', 'storage-test') as tracker:
    tracker.record_tokens({'total': 100, 'input': 60, 'output': 40})
    tracker.record_cost(0.001)"

# Check storage worked
ls -la .llm-telemetry/$(date +%Y-%m-%d)/
cat .llm-telemetry/$(date +%Y-%m-%d)/telemetry.jsonl

# Test CLI
llm-telemetry stats --days=7
```

## Git Workflow

```bash
# Create feature branch
gt create --all -m "feat: add local telemetry storage (v0.2.0)"

# After implementation
just test
just ci

# Commit and push
gt modify -m "feat: implement LocalStorage class with JSONL backend"
gt modify -m "feat: integrate storage with AITelemetryTracker"
gt modify -m "feat: add CLI query tools"
gt submit

# After PR approval, land a commit on main with a `feat:`/`fix:` prefix (or `BREAKING`)
# CI success will trigger the Release workflow to bump versions and tag automatically.
# Monitor GitHub Actions for completion.
```

## Success Criteria

### Storage
- [ ] Telemetry saved to `.llm-telemetry/YYYY-MM-DD/telemetry.jsonl`
- [ ] Old data (>30 days) automatically cleaned up
- [ ] Storage adds <10ms overhead to AI calls
- [ ] Thread-safe for concurrent writes

### Client Abstractions
- [ ] Unified interface for Anthropic, OpenRouter, OpenAI
- [ ] Auto-detects available API keys
- [ ] Telemetry automatically tracked for all calls
- [ ] Existing ai_client.py can be replaced with new client
- [ ] Existing OpenRouterClient can be replaced

### Model Registry
- [ ] All models from ai_client.py migrated
- [ ] Model selection by alias works ("haiku" → "claude-3-5-haiku")
- [ ] Accurate pricing and capabilities

### CLI & Testing
- [ ] CLI can query costs and usage stats
- [ ] All existing v0.1.0 tests still pass
- [ ] New tests for storage, clients, registry
- [ ] Works in spacewalker, mimir, and new projects

### Migration
- [ ] Drop-in replacement for existing AI clients
- [ ] No breaking changes to telemetry
- [ ] Clear migration guide in documentation

## Questions/Decisions

1. **JSONL vs SQLite?** → Start with JSONL for simplicity, SQLite in v0.3.0
2. **Compression?** → Not yet, add in v0.3.0 if needed
3. **Encryption?** → No, rely on filesystem permissions
4. **Multi-project?** → Each project stores its own `.llm-telemetry/`

## Time Estimate

- Storage module: 3-4 hours
- Client abstractions: 4-5 hours
- Model registry: 2-3 hours
- Common utilities: 2-3 hours
- Integration: 2-3 hours
- CLI tools: 2-3 hours
- Tests & docs: 3-4 hours
- **Total: 2-3 days** (or 1 week part-time)

---

Ready to implement? Start with the LocalStorage class and work your way through the checklist!