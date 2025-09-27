"""Tests for telemetry functionality"""
from unittest.mock import Mock, patch
from llm_cli_core import (
    track_ai_call,
    OpenRouterTokens,
    AnthropicTokens,
    OpenAITokens,
    AITelemetryTracker,
    TokenData,
)


def test_track_ai_call_context_manager():
    """Test basic telemetry tracking with context manager"""
    with track_ai_call("test-agent", "test-operation") as tracker:
        assert tracker.agent_name == "test-agent"
        assert tracker.operation == "test-operation"
        assert tracker.start_time is not None


def test_openrouter_token_extraction():
    """Test OpenRouter token extraction"""
    response = {
        "usage": {
            "total_tokens": 100,
            "prompt_tokens": 60,
            "completion_tokens": 40,
        }
    }
    tokens = OpenRouterTokens(response)
    assert tokens.data.total == 100
    assert tokens.data.input == 60
    assert tokens.data.output == 40


def test_anthropic_token_extraction():
    """Test Anthropic token extraction"""
    # Mock Anthropic response object
    mock_response = Mock()
    mock_response.usage.input_tokens = 50
    mock_response.usage.output_tokens = 30

    tokens = AnthropicTokens(mock_response)
    assert tokens.data.total == 80
    assert tokens.data.input == 50
    assert tokens.data.output == 30


def test_anthropic_token_extraction_no_usage():
    """Test Anthropic token extraction with no usage attribute"""
    mock_response = Mock(spec=[])  # No usage attribute
    tokens = AnthropicTokens(mock_response)
    assert tokens.data.total == 0
    assert tokens.data.input == 0
    assert tokens.data.output == 0


def test_openai_token_extraction():
    """Test OpenAI token extraction"""
    response = {
        "usage": {
            "total_tokens": 150,
            "prompt_tokens": 100,
            "completion_tokens": 50,
        }
    }
    tokens = OpenAITokens(response)
    assert tokens.data.total == 150
    assert tokens.data.input == 100
    assert tokens.data.output == 50


def test_telemetry_tracker_initialization():
    """Test AITelemetryTracker initialization"""
    tracker = AITelemetryTracker("my-agent", "my-operation")
    assert tracker.agent_name == "my-agent"
    assert tracker.operation == "my-operation"
    assert tracker.start_time is None
    assert tracker.tokens == TokenData()
    assert tracker.cost == 0.0
    assert tracker.model == "unknown"
    assert tracker.success is True


def test_telemetry_tracker_record_methods():
    """Test AITelemetryTracker recording methods"""
    tracker = AITelemetryTracker("test-agent", "test-op")

    # Test recording tokens
    response = {"usage": {"total_tokens": 100, "prompt_tokens": 60, "completion_tokens": 40}}
    tracker.record_tokens(OpenRouterTokens(response))
    assert tracker.tokens.total == 100
    assert tracker.tokens.input == 60
    assert tracker.tokens.output == 40

    # Test recording cost
    tracker.record_cost(0.005)
    assert tracker.cost == 0.005

    # Test recording model
    tracker.record_model("gpt-4")
    assert tracker.model == "gpt-4"


@patch('requests.post')
def test_send_metrics(mock_post):
    """Test sending metrics to pushgateway"""
    mock_post.return_value.status_code = 200

    tracker = AITelemetryTracker("test-agent", "test-op")
    tracker.start()
    result = tracker.send_metrics()

    assert result is True
    mock_post.assert_called_once()


@patch('requests.post')
def test_send_metrics_failure(mock_post):
    """Test handling of metrics send failure"""
    mock_post.return_value.status_code = 500

    tracker = AITelemetryTracker("test-agent", "test-op")
    tracker.start()
    result = tracker.send_metrics()

    assert result is False


def test_legacy_send_agent_metrics():
    """Test legacy send_agent_metrics function"""
    from llm_cli_core import send_agent_metrics

    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200

        result = send_agent_metrics(
            agent_name="test-agent",
            operation="test-op",
            duration_ms=1000,
            token_count=100,
            input_tokens=60,
            output_tokens=40,
            cost_usd=0.001,
            model="gpt-4",
            success=True,
        )

        assert result is True
        mock_post.assert_called_once()
