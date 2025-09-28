# 🎯 HANDOFF: Implement Local Telemetry Storage v0.2.0

## Your Mission
Add local file-based storage to llm-cli-tools-core so telemetry data is saved to disk for later analysis. Currently, telemetry only goes to Prometheus. We want to ALSO store it locally.

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

### 3. Create CLI Query Tool
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

1. **Start with storage module**
   - Create the LocalStorage class
   - Implement JSONL writing with proper locking
   - Test with simple script

2. **Integrate with tracker**
   - Modify AITelemetryTracker.send_metrics()
   - Add new record_prompt() and record_response() methods
   - Test with existing tools

3. **Add CLI tools**
   - Basic stats command first
   - Cost analysis second
   - Make it installable via pyproject.toml entry point

4. **Test thoroughly**
   - Unit tests for storage operations
   - Integration test with real AI calls
   - Performance test (should add <10ms overhead)

5. **Update documentation**
   - Update README with storage features
   - Add examples of querying data
   - Document privacy considerations

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

# After PR approval, create release
git tag v0.2.0
git push origin v0.2.0
```

## Success Criteria

- [ ] Storage writes telemetry to `.llm-telemetry/YYYY-MM-DD/telemetry.jsonl`
- [ ] Old data (>30 days) is automatically cleaned up
- [ ] Storage adds <10ms overhead to AI calls
- [ ] Thread-safe for concurrent writes
- [ ] CLI can query costs and usage stats
- [ ] All existing tests still pass
- [ ] New storage tests pass
- [ ] Works in both spacewalker and mimir without changes

## Questions/Decisions

1. **JSONL vs SQLite?** → Start with JSONL for simplicity, SQLite in v0.3.0
2. **Compression?** → Not yet, add in v0.3.0 if needed
3. **Encryption?** → No, rely on filesystem permissions
4. **Multi-project?** → Each project stores its own `.llm-telemetry/`

## Time Estimate

- Storage module: 2-3 hours
- Integration: 1 hour
- CLI tools: 2 hours
- Tests: 2 hours
- **Total: ~8 hours**

---

Ready to implement? Start with the LocalStorage class and work your way through the checklist!