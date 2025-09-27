#!/usr/bin/env python3
"""
AI Telemetry - Unified monitoring for all AI integrations

This module provides a standardized way to:
1. Extract tokens from different AI API responses
2. Detect Claude Code session information
3. Send telemetry metrics to monitoring stack
4. Handle errors gracefully

Usage:
    from ai_telemetry import track_ai_call, OpenRouterTokens, AnthropicTokens

    # Method 1: Context manager (recommended)
    with track_ai_call("my-agent", "document_search") as tracker:
        response = openrouter_client.post(...)
        tracker.record_tokens(OpenRouterTokens(response.json()))
        tracker.record_cost(0.003)

    # Method 2: Manual tracking
    tracker = AITelemetryTracker("my-agent", "analysis")
    tracker.start()
    # ... make AI call ...
    tracker.record_response(AnthropicTokens(response), cost=0.005)
    tracker.send_metrics()
"""

import os
import time
import logging
from typing import Dict, Any, Union, NamedTuple
from dataclasses import dataclass
from contextlib import contextmanager

# Configure logging
logger = logging.getLogger(__name__)


class TokenData(NamedTuple):
    """Standardized token data structure"""

    total: int = 0
    input: int = 0
    output: int = 0


@dataclass
class SessionInfo:
    """Claude Code session information"""

    session_id: str
    user_id: str
    working_directory: str
    start_time: str

    @classmethod
    def detect(cls) -> "SessionInfo":
        """Detect session info using environment variables (more reliable than SDK)"""
        # Try Claude Code environment variables first
        session_id = os.getenv("CLAUDE_SESSION_ID")
        user_id = os.getenv("CLAUDE_USER_ID") or os.getenv("USER", "unknown")

        # Fallback: generate pseudo-session from environment
        if not session_id:
            import hashlib

            env_data = (
                f"{user_id}-{os.getcwd()}-{time.time()//3600}"  # Hour-based sessions
            )
            # Format: "env-{8-char-hash}" where hash is MD5 of user+directory+hour
            # Example: "env-a1b2c3d4" - provides session continuity within same hour
            session_id = f"env-{hashlib.md5(env_data.encode()).hexdigest()[:8]}"

        return cls(
            session_id=session_id,
            user_id=user_id,
            working_directory=os.getcwd(),
            start_time=time.strftime("%Y-%m-%d %H:%M:%S"),
        )


# Token Extractors for Different APIs
class OpenRouterTokens:
    """Extract tokens from OpenRouter API response"""

    def __init__(self, response_json: Dict[str, Any]):
        usage = response_json.get("usage", {})
        self.data = TokenData(
            total=usage.get("total_tokens", 0),
            input=usage.get("prompt_tokens", 0),
            output=usage.get("completion_tokens", 0),
        )


class AnthropicTokens:
    """Extract tokens from Anthropic API response"""

    def __init__(self, response):
        if hasattr(response, "usage"):
            self.data = TokenData(
                total=response.usage.input_tokens + response.usage.output_tokens,
                input=response.usage.input_tokens,
                output=response.usage.output_tokens,
            )
        else:
            self.data = TokenData()


class OpenAITokens:
    """Extract tokens from OpenAI/compatible API response"""

    def __init__(self, response_json: Dict[str, Any]):
        usage = response_json.get("usage", {})
        self.data = TokenData(
            total=usage.get("total_tokens", 0),
            input=usage.get("prompt_tokens", 0),
            output=usage.get("completion_tokens", 0),
        )


class AITelemetryTracker:
    """Tracks AI operations and sends telemetry data"""

    def __init__(self, agent_name: str, operation: str):
        self.agent_name = agent_name
        self.operation = operation
        self.start_time = None
        self.tokens = TokenData()
        self.cost = 0.0
        self.model = "unknown"
        self.success = True
        self.session_info = SessionInfo.detect()

    def start(self):
        """Start timing the operation"""
        self.start_time = time.time()

    def record_tokens(
        self, token_extractor: Union[OpenRouterTokens, AnthropicTokens, OpenAITokens]
    ):
        """Record token usage from API response"""
        self.tokens = token_extractor.data

    def record_cost(self, cost: float):
        """Record operation cost"""
        self.cost = cost

    def record_model(self, model: str):
        """Record AI model used"""
        self.model = model

    def record_response(
        self,
        token_extractor,
        cost: float = 0.0,
        model: str = "unknown",
        success: bool = True,
    ):
        """Record complete response data"""
        self.record_tokens(token_extractor)
        self.record_cost(cost)
        self.record_model(model)
        self.success = success

    def send_metrics(self, pushgateway_url: str = "http://localhost:7101") -> bool:
        """Send telemetry metrics to monitoring stack"""
        if self.start_time is None:
            logger.warning(
                "Telemetry tracker was never started - cannot calculate duration"
            )
            return False

        duration_ms = int((time.time() - self.start_time) * 1000)

        try:
            import requests

            timestamp_id = int(time.time() * 1000)
            session_id = self.session_info.session_id
            user_id = self.session_info.user_id

            url = f"{pushgateway_url}/metrics/job/ai_agents/agent/{self.agent_name}/session_id/{session_id}/user_id/{user_id}/timestamp/{timestamp_id}"

            # Enhanced metrics with user correlation (proper pushgateway format)
            metrics = f"""ai_agent_usage_total{{agent_name="{self.agent_name}",operation="{self.operation}",model="{self.model}",success="{self.success}",user="{user_id}"}} 1
ai_agent_duration_ms_total{{agent_name="{self.agent_name}",session_id="{session_id}",user="{user_id}"}} {duration_ms}
ai_agent_tokens_total{{agent_name="{self.agent_name}",model="{self.model}",user="{user_id}"}} {self.tokens.total}
ai_agent_input_tokens_total{{agent_name="{self.agent_name}",model="{self.model}",user="{user_id}"}} {self.tokens.input}
ai_agent_output_tokens_total{{agent_name="{self.agent_name}",model="{self.model}",user="{user_id}"}} {self.tokens.output}
ai_agent_cost_usd_total{{agent_name="{self.agent_name}",model="{self.model}",user="{user_id}"}} {self.cost}
ai_agent_sessions_total{{session_id="{session_id}",user="{user_id}",working_directory="{self.session_info.working_directory}"}} 1
"""

            response = requests.post(
                url, data=metrics, headers={"Content-Type": "text/plain"}, timeout=5
            )
            success = response.status_code == 200

            if success:
                logger.debug(
                    f"Telemetry sent: {self.agent_name} {self.operation} ({duration_ms}ms, {self.tokens.total} tokens)"
                )
            else:
                logger.warning(f"Telemetry failed: HTTP {response.status_code}")

            return success

        except Exception as e:
            logger.warning(f"Telemetry error: {e}")
            return False


@contextmanager
def track_ai_call(agent_name: str, operation: str):
    """Context manager for easy AI call tracking

    Usage:
        with track_ai_call("doc-finder", "search") as tracker:
            response = api_call()
            tracker.record_tokens(OpenRouterTokens(response.json()))
            tracker.record_cost(0.003)
    """
    tracker = AITelemetryTracker(agent_name, operation)
    tracker.start()

    try:
        yield tracker
    except Exception:
        tracker.success = False
        raise
    finally:
        tracker.send_metrics()


# Legacy compatibility function
def send_agent_metrics(
    agent_name: str,
    operation: str,
    duration_ms: int,
    token_count: int = 0,
    input_tokens: int = 0,
    output_tokens: int = 0,
    cost_usd: float = 0.0,
    model: str = "unknown",
    success: bool = True,
    pushgateway_url: str = "http://localhost:7101",
) -> bool:
    """Legacy compatibility function - use track_ai_call() for new integrations"""
    logger.warning(
        "Using legacy send_agent_metrics(). Consider upgrading to track_ai_call()."
    )

    tracker = AITelemetryTracker(agent_name, operation)
    tracker.start_time = time.time() - (duration_ms / 1000)  # Reconstruct start time
    tracker.tokens = TokenData(
        total=token_count, input=input_tokens, output=output_tokens
    )
    tracker.cost = cost_usd
    tracker.model = model
    tracker.success = success

    return tracker.send_metrics(pushgateway_url)


def show_help():
    """Display usage help"""
    print(__doc__)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AI Telemetry Library")
    parser.add_argument("action", nargs="?", choices=["help", "test"], default="help")
    args = parser.parse_args()

    if args.action == "help":
        show_help()
    elif args.action == "test":
        print("🧪 Testing AI Telemetry...")

        # Test session detection
        session = SessionInfo.detect()
        print(f"✅ Session: {session.session_id} (User: {session.user_id})")

        # Test token extraction
        mock_openrouter = {
            "usage": {"total_tokens": 100, "prompt_tokens": 60, "completion_tokens": 40}
        }
        tokens = OpenRouterTokens(mock_openrouter)
        print(f"✅ Token extraction: {tokens.data}")

        # Test metrics sending
        with track_ai_call("test-agent", "test-operation") as tracker:
            time.sleep(0.01)  # Simulate work
            tracker.record_tokens(OpenRouterTokens(mock_openrouter))
            tracker.record_cost(0.001)
            tracker.record_model("test-model")

        print("✅ Telemetry test completed")
