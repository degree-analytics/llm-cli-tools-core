"""llm-cli-tools-core - Core telemetry and utilities for LLM CLI tools"""

from .telemetry.core import (
    AITelemetryTracker,
    track_ai_call,
    send_agent_metrics,  # Legacy compatibility
    TokenData,
    SessionInfo,
    OpenRouterTokens,
    AnthropicTokens,
    OpenAITokens,
)

__version__ = "0.1.0"

__all__ = [
    "AITelemetryTracker",
    "track_ai_call",
    "send_agent_metrics",
    "TokenData",
    "SessionInfo",
    "OpenRouterTokens",
    "AnthropicTokens",
    "OpenAITokens",
]