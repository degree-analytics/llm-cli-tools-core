# llm-cli-tools-core v0.2.0 - Local Telemetry Storage

## 🎯 Goal
Implement local file-based storage for AI telemetry data that can be mined later for insights, cost analysis, and performance optimization.

## 📋 Requirements

### Core Storage Features
1. **JSON-based storage** in configurable directory (default: `.llm-telemetry/`)
2. **Per-day organization** for easy archival and analysis
3. **Automatic rotation** to prevent unbounded growth
4. **Thread-safe writes** for concurrent operations
5. **Minimal overhead** - must not slow down AI operations

### What to Store
Each AI call should save:
```json
{
  "timestamp": "2025-01-27T10:30:45.123Z",
  "agent_name": "doc-finder",
  "operation": "search",
  "model": "claude-3-5-haiku",
  "session_id": "abc123",
  "user_id": "chadwalters",
  "duration_ms": 1234,
  "tokens": {
    "input": 500,
    "output": 200,
    "total": 700
  },
  "cost_usd": 0.0025,
  "success": true,
  "prompt_hash": "sha256:abc...",  // Hash of prompt for deduplication
  "response_hash": "sha256:def...", // Hash of response for analysis
  "metadata": {
    "project": "spacewalker",  // Auto-detected from cwd
    "git_branch": "main",      // Optional git context
    "error": null              // Error message if failed
  }
}
```

### Optional Storage (configured via env)
```json
{
  "prompt": "...",     // Only if LLM_STORE_PROMPTS=true
  "response": "...",   // Only if LLM_STORE_RESPONSES=true
}
```

## 📁 Storage Structure

```
.llm-telemetry/                    # Configurable via LLM_TELEMETRY_DIR
├── 2025-01-27/                    # Daily directories
│   ├── telemetry.jsonl           # Core metrics (always stored)
│   ├── prompts.jsonl             # Optional prompt storage
│   └── responses.jsonl           # Optional response storage
├── 2025-01-28/
│   └── telemetry.jsonl
└── summary.json                   # Rolling summary stats
```

## 🔧 Implementation Plan

### Phase 1: Core Storage (MVP)
```python
# llm_cli_core/storage/local.py
class LocalStorage:
    def __init__(self, base_dir: Path = None):
        self.base_dir = Path(os.getenv("LLM_TELEMETRY_DIR", ".llm-telemetry"))

    def store_telemetry(self, data: Dict[str, Any]) -> bool:
        """Store telemetry data in daily JSONL file"""

    def get_today_stats(self) -> Dict[str, Any]:
        """Get today's usage statistics"""

    def query_by_date_range(self, start: date, end: date) -> List[Dict]:
        """Query telemetry by date range"""
```

### Phase 2: Integration
```python
# Modify llm_cli_core/telemetry/core.py
class AITelemetryTracker:
    def send_metrics(self):
        # Existing Prometheus code...

        # NEW: Also store locally
        if os.getenv("LLM_TELEMETRY_STORAGE", "true").lower() == "true":
            storage = LocalStorage()
            storage.store_telemetry(self.to_dict())
```

### Phase 3: Query Tools
```python
# llm_cli_core/cli.py - New CLI for querying
"""
Usage:
  llm-telemetry stats today              # Today's usage
  llm-telemetry stats week               # This week's usage
  llm-telemetry costs --days=7           # Cost analysis
  llm-telemetry models --top=5           # Most used models
  llm-telemetry agents                   # Usage by agent
"""
```

## 🔐 Environment Configuration

```bash
# .env configuration
LLM_TELEMETRY_STORAGE=true           # Enable local storage (default: true)
LLM_TELEMETRY_DIR=.llm-telemetry     # Storage directory (default: .llm-telemetry)
LLM_STORE_PROMPTS=false              # Store full prompts (default: false)
LLM_STORE_RESPONSES=false            # Store full responses (default: false)
LLM_RETENTION_DAYS=30                # Keep data for N days (default: 30)
LLM_STORAGE_MAX_SIZE_MB=100          # Max storage size in MB (default: 100)
```

## 🚀 Migration Path

### For existing users (v0.1.0 → v0.2.0)
1. **No breaking changes** - Prometheus metrics continue to work
2. **Storage is opt-in** - Set `LLM_TELEMETRY_STORAGE=false` to disable
3. **Automatic** - Just upgrade and storage starts working

### Example upgrade:
```bash
# In spacewalker or mimir
pip install --upgrade git+https://github.com/chadwalters/llm-cli-tools-core.git@v0.2.0

# Add to .env if you want custom location
echo "LLM_TELEMETRY_DIR=.metrics/ai" >> .env

# That's it! Storage starts automatically
```

## 📊 Use Cases

### 1. Cost Analysis
```bash
$ llm-telemetry costs --days=30
📊 Last 30 days:
  Total cost: $47.32
  By model:
    - claude-3-5-haiku: $12.45 (74%)
    - claude-sonnet-4: $34.87 (26%)
  By project:
    - spacewalker: $31.20
    - mimir: $16.12
```

### 2. Performance Monitoring
```bash
$ llm-telemetry performance
⚡ Performance Stats:
  Average response time: 1.2s
  P95 response time: 3.4s
  Slowest operations:
    - doc-search (complex): 5.2s avg
    - code-analysis: 3.1s avg
```

### 3. Usage Patterns
```bash
$ llm-telemetry patterns
🔍 Usage Patterns:
  Peak hours: 10am-12pm, 2pm-4pm
  Most active day: Tuesday
  Common operations:
    - git-pr-review: 145 calls
    - doc-search: 89 calls
    - test-generation: 67 calls
```

## ✅ Success Criteria

1. **Zero config works** - Storage enabled by default with sensible defaults
2. **No performance impact** - Async/thread-safe writes don't block AI calls
3. **Easy to query** - Simple CLI tools to analyze stored data
4. **Bounded growth** - Automatic cleanup of old data
5. **Privacy-aware** - Prompts/responses optional and off by default

## 🚫 What NOT to Include (Yet)

- ❌ Database backends (SQLite, PostgreSQL) - Keep it simple with JSON
- ❌ Cloud storage (S3, GCS) - Local only for now
- ❌ Real-time dashboards - Just CLI queries for now
- ❌ Multi-project aggregation - Each project stores its own data
- ❌ Encryption - Rely on filesystem permissions

## 📅 Timeline Estimate

- **Core storage implementation**: 2-3 hours
- **Integration with existing tracker**: 1 hour
- **CLI query tools**: 2-3 hours
- **Tests and documentation**: 2 hours
- **Total**: ~1 day of focused work

## 🎯 Next Steps After v0.2.0

### v0.3.0 - Advanced Queries
- SQL-like query language
- Export to CSV/Excel
- Aggregation across projects

### v0.4.0 - Visualization
- Simple HTML reports
- Cost trend charts
- Model usage heatmaps

### v0.5.0 - Optimization
- SQLite backend option for better performance
- Compression for old data
- Incremental summaries for faster queries