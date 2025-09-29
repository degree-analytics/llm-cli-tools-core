# llm-cli-tools-core v0.2.0 - Storage + Client Abstractions

## 🎯 Goals
1. **Local Telemetry Storage** - Save telemetry to disk for later analysis
2. **LLM Client Abstractions** - Unified interface for Anthropic, OpenRouter, OpenAI
3. **Model Registry** - Centralized model configurations and capabilities
4. **Common Utilities** - Token estimation, retry logic, cost calculation

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

## 🤖 LLM Client Abstractions

### Base Client Interface
```python
# llm_cli_core/clients/base.py
class BaseLLMClient:
    """Abstract base class for all LLM providers"""

    def chat(self, prompt: str, system: str = None, **kwargs) -> LLMResponse:
        """Send chat request to LLM"""

    def stream(self, prompt: str, system: str = None, **kwargs):
        """Stream responses from LLM"""

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text"""

    def calculate_cost(self, tokens: TokenData) -> float:
        """Calculate cost based on token usage"""
```

### Provider Implementations
```python
# llm_cli_core/clients/anthropic_client.py
class AnthropicClient(BaseLLMClient):
    """Anthropic Claude API client"""
    def __init__(self, api_key: str = None, model: str = "claude-3-5-haiku"):
        # Support for Claude 3.5 Haiku, Sonnet 4, Opus 4

# llm_cli_core/clients/openrouter_client.py
class OpenRouterClient(BaseLLMClient):
    """OpenRouter multi-model API client"""
    def __init__(self, api_key: str = None, model: str = "meta-llama/llama-3.1-8b-instruct:free"):
        # Support for 100+ models via OpenRouter

# llm_cli_core/clients/openai_client.py
class OpenAIClient(BaseLLMClient):
    """OpenAI GPT API client"""
    def __init__(self, api_key: str = None, model: str = "gpt-4-turbo"):
        # Support for GPT-4, GPT-3.5, etc.
```

### Client Factory
```python
# llm_cli_core/clients/__init__.py
def get_client(provider: str = "auto", model: str = None) -> BaseLLMClient:
    """
    Get appropriate client based on available API keys

    Priority order:
    1. Explicit provider requested
    2. ANTHROPIC_API_KEY → AnthropicClient
    3. OPENROUTER_API_KEY → OpenRouterClient
    4. OPENAI_API_KEY → OpenAIClient
    """
```

## 📊 Model Registry

### Model Configuration
```python
# llm_cli_core/models/registry.py
MODEL_REGISTRY = {
    # Anthropic Models
    "claude-3-5-haiku": {
        "provider": "anthropic",
        "context_window": 200000,
        "max_output": 8192,
        "pricing": {"input": 0.25, "output": 1.25},  # per 1M tokens
        "capabilities": ["vision", "function_calling"],
        "recommended_for": ["simple_tasks", "high_volume"]
    },
    "claude-sonnet-4": {
        "provider": "anthropic",
        "context_window": 200000,
        "max_output": 8192,
        "pricing": {"input": 3.0, "output": 15.0},
        "capabilities": ["vision", "function_calling", "reasoning"],
        "recommended_for": ["complex_analysis", "code_generation"]
    },

    # OpenRouter Models
    "llama-3.1-70b": {
        "provider": "openrouter",
        "context_window": 131072,
        "max_output": 4096,
        "pricing": {"input": 0.59, "output": 0.79},
        "capabilities": ["reasoning"],
        "recommended_for": ["open_source", "cost_effective"]
    },

    # ... more models
}

def select_model(requirements: Dict) -> str:
    """
    Auto-select best model based on requirements:
    - budget_per_call: Maximum cost willing to pay
    - min_context: Minimum context window needed
    - capabilities: Required capabilities (vision, etc)
    - speed_priority: Prefer faster models
    """
```

## 🔧 Common Utilities

### Token Estimation
```python
# llm_cli_core/utils/tokens.py
def estimate_tokens(text: str, model: str = None) -> int:
    """
    Estimate token count for text
    Uses tiktoken for OpenAI, claude-tokenizer for Anthropic
    Falls back to character-based estimation
    """

def truncate_to_tokens(text: str, max_tokens: int, model: str = None) -> str:
    """Truncate text to fit within token limit"""
```

### Retry Logic
```python
# llm_cli_core/utils/retry.py
def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    backoff_factor: float = 2.0,
    exceptions: Tuple = (APIError, RateLimitError)
):
    """Generic retry decorator with exponential backoff"""
```

### Prompt Caching
```python
# llm_cli_core/utils/cache.py
class PromptCache:
    """
    Cache prompts for Anthropic beta caching
    Reduces cost for repeated system prompts
    """
    def get_cached_messages(self, messages: List[Dict]) -> List[Dict]:
        """Add cache_control to eligible messages"""
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

### Phase 2: LLM Clients
```python
# Implement base client and provider clients
# Move existing AIClient and OpenRouterClient logic here
# Add proper error handling and retry logic
```

### Phase 3: Model Registry
```python
# Create comprehensive model registry
# Import MODEL_CAPABILITIES and MODEL_PRICING from existing code
# Add model selection logic
```

### Phase 4: Integration
```python
# Update telemetry to use new clients
class AITelemetryTracker:
    def send_metrics(self):
        # Existing Prometheus code...

        # NEW: Also store locally
        if os.getenv("LLM_TELEMETRY_STORAGE_ENABLED", "true").lower() == "true":
            storage = LocalStorage()
            storage.store_telemetry(self.to_dict())
```

### Phase 5: Query Tools
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
LLM_TELEMETRY_STORAGE_ENABLED=true   # Enable local storage (default: true)
LLM_TELEMETRY_DIR=.llm-telemetry     # Storage directory (default: .llm-telemetry)
LLM_STORE_PROMPTS=false              # Store full prompts (default: false)
LLM_STORE_RESPONSES=false            # Store full responses (default: false)
LLM_RETENTION_DAYS=30                # Keep data for N days (default: 30)
LLM_STORAGE_MAX_SIZE_MB=100          # Max storage size in MB (default: 100)
```

## 🚀 Migration Path

### For existing users (v0.1.0 → v0.2.0)
1. **No breaking changes** - Telemetry continues to work
2. **Storage is automatic** - Set `LLM_TELEMETRY_STORAGE_ENABLED=false` to disable
3. **New client abstractions** - Gradually migrate from direct client usage

### Migration Examples

#### Before (Direct Client Usage)
```python
# Old way in ai_client.py
import anthropic
client = anthropic.Client()
response = client.messages.create(...)
```

#### After (Unified Interface)
```python
# New way with llm-cli-tools-core
from llm_cli_core import get_client

client = get_client()  # Auto-detects available API keys
response = client.chat("Generate a commit message", system="You are a git expert")
# Telemetry automatically tracked!
```

#### Storage Integration
```bash
# In spacewalker or mimir
pip install --upgrade git+https://github.com/degree-analytics/llm-cli-tools-core.git@v0.2.0

# Configure storage location (optional)
echo "LLM_TELEMETRY_DIR=.metrics/ai" >> .env

# Use new client (auto-tracks telemetry with storage)
from llm_cli_core import get_client
client = get_client(model="claude-3-5-haiku")
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

### Storage
1. **Zero config works** - Storage enabled by default with sensible defaults
2. **No performance impact** - Async/thread-safe writes don't block AI calls
3. **Easy to query** - Simple CLI tools to analyze stored data
4. **Bounded growth** - Automatic cleanup of old data
5. **Privacy-aware** - Prompts/responses optional and off by default

### Client Abstractions
1. **Provider agnostic** - Same interface for Anthropic, OpenRouter, OpenAI
2. **Auto-detection** - Finds available API keys automatically
3. **Integrated telemetry** - All calls tracked automatically
4. **Error handling** - Consistent retry logic and error messages
5. **Model flexibility** - Easy to switch models or providers

### Model Registry
1. **Comprehensive** - All major models documented
2. **Auto-selection** - Choose best model for requirements
3. **Cost tracking** - Accurate pricing for all models
4. **Capability matching** - Find models with needed features

## 🚫 What NOT to Include (Yet)

- ❌ Database backends (SQLite, PostgreSQL) - Keep it simple with JSON
- ❌ Cloud storage (S3, GCS) - Local only for now
- ❌ Real-time dashboards - Just CLI queries for now
- ❌ Multi-project aggregation - Each project stores its own data
- ❌ Streaming responses - Focus on complete responses first
- ❌ Fine-tuned models - Just base models for now
- ❌ Multi-modal beyond text - Text focus (vision later)

## 📅 Timeline Estimate

- **Core storage implementation**: 3-4 hours
- **LLM client abstractions**: 4-5 hours
- **Model registry**: 2-3 hours
- **Common utilities**: 2-3 hours
- **Integration & migration**: 2-3 hours
- **CLI query tools**: 2-3 hours
- **Tests and documentation**: 3-4 hours
- **Total**: ~2-3 days of focused work

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