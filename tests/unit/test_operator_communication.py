"""Unit tests for operator communication tool."""

# Standard library imports
from unittest.mock import patch, call, MagicMock

# Third-party imports
import pytest

# Local application imports
from contreact_ollama.tools.operator_communication import send_message_to_operator
from contreact_ollama.core.config import ExperimentConfig


# ===== Backward Compatibility Tests (No Config) =====

def test_send_message_no_config_uses_terminal():
    """Test backward compatibility - no config defaults to terminal."""
    with patch('contreact_ollama.tools.operator_communication.TerminalChannel') as mock_terminal:
        instance = MagicMock()
        instance.send_and_wait.return_value = "response"
        mock_terminal.return_value = instance
        
        result = send_message_to_operator("What should I do?")
        
        # Verify TerminalChannel was created
        mock_terminal.assert_called_once()
        
        # Verify send_and_wait was called with defaults
        instance.send_and_wait.assert_called_once_with("What should I do?", "unknown", 0)
        
        assert result == "response"


def test_send_message_prints_agent_prefix_backward_compat(capsys):
    """Test that send_message_to_operator prints message with agent prefix (backward compat)."""
    with patch('builtins.input', return_value='operator response'):
        result = send_message_to_operator("What should I do?")
        
        # Verify message printed with context
        captured = capsys.readouterr()
        assert "[AGENT - unknown | Cycle 0]: What should I do?" in captured.out
        assert result == "operator response"


def test_send_message_returns_operator_input_backward_compat():
    """Test that send_message_to_operator returns operator's response (backward compat)."""
    with patch('builtins.input', return_value='operator response'):
        result = send_message_to_operator("message")
        assert result == "operator response"


# ===== Terminal Channel Selection Tests =====

def test_send_message_telegram_disabled_uses_terminal():
    """Test terminal is used when telegram_enabled=False."""
    config = ExperimentConfig(
        run_id="test-run",
        model_name="test-model",
        cycle_count=1,
        ollama_client_config={"host": "http://localhost:11434"},
        model_options={},
        telegram_enabled=False
    )
    
    with patch('contreact_ollama.tools.operator_communication.TerminalChannel') as mock_terminal:
        instance = MagicMock()
        instance.send_and_wait.return_value = "terminal response"
        mock_terminal.return_value = instance
        
        result = send_message_to_operator("Test message", config, "run-001", 5)
        
        # Verify TerminalChannel was used
        mock_terminal.assert_called_once()
        instance.send_and_wait.assert_called_once_with("Test message", "run-001", 5)
        
        assert result == "terminal response"


def test_send_message_config_none_uses_terminal():
    """Test terminal is used when config=None."""
    with patch('contreact_ollama.tools.operator_communication.TerminalChannel') as mock_terminal:
        instance = MagicMock()
        instance.send_and_wait.return_value = "terminal response"
        mock_terminal.return_value = instance
        
        result = send_message_to_operator("Test", None, "run-001", 5)
        
        mock_terminal.assert_called_once()
        instance.send_and_wait.assert_called_once_with("Test", "run-001", 5)


# ===== Telegram Channel Selection Tests =====

def test_send_message_telegram_enabled_uses_telegram():
    """Test Telegram is used when telegram_enabled=True."""
    config = ExperimentConfig(
        run_id="test-run",
        model_name="test-model",
        cycle_count=1,
        ollama_client_config={"host": "http://localhost:11434"},
        model_options={},
        telegram_enabled=True,
        telegram_authorized_users=[123456789],
        telegram_timeout_minutes=5
    )
    
    with patch('contreact_ollama.tools.operator_communication.TelegramChannel') as mock_telegram:
        instance = MagicMock()
        instance.send_and_wait.return_value = "telegram response"
        mock_telegram.return_value = instance
        
        result = send_message_to_operator("Test message", config, "run-001", 5)
        
        # Verify TelegramChannel was created with config
        mock_telegram.assert_called_once_with(
            authorized_users=[123456789],
            timeout_minutes=5
        )
        
        # Verify send_and_wait was called
        instance.send_and_wait.assert_called_once_with("Test message", "run-001", 5)
        
        assert result == "telegram response"


# ===== Fallback Behavior Tests =====

def test_send_message_telegram_connection_error_falls_back_to_terminal():
    """Test fallback to terminal when Telegram connection fails."""
    config = ExperimentConfig(
        run_id="test-run",
        model_name="test-model",
        cycle_count=1,
        ollama_client_config={"host": "http://localhost:11434"},
        model_options={},
        telegram_enabled=True,
        telegram_authorized_users=[123456789],
        telegram_timeout_minutes=5
    )
    
    with patch('contreact_ollama.tools.operator_communication.TelegramChannel') as mock_telegram, \
         patch('contreact_ollama.tools.operator_communication.TerminalChannel') as mock_terminal:
        
        # Telegram fails with ConnectionError
        mock_telegram.side_effect = ConnectionError("Connection failed")
        
        # Terminal succeeds
        terminal_instance = MagicMock()
        terminal_instance.send_and_wait.return_value = "terminal fallback response"
        mock_terminal.return_value = terminal_instance
        
        result = send_message_to_operator("Test", config, "run-001", 5)
        
        # Verify fallback to terminal
        mock_terminal.assert_called_once()
        terminal_instance.send_and_wait.assert_called_once_with("Test", "run-001", 5)
        
        assert result == "terminal fallback response"


def test_send_message_telegram_timeout_falls_back_to_terminal():
    """Test fallback to terminal when Telegram times out."""
    config = ExperimentConfig(
        run_id="test-run",
        model_name="test-model",
        cycle_count=1,
        ollama_client_config={"host": "http://localhost:11434"},
        model_options={},
        telegram_enabled=True,
        telegram_authorized_users=[123456789],
        telegram_timeout_minutes=5
    )
    
    with patch('contreact_ollama.tools.operator_communication.TelegramChannel') as mock_telegram, \
         patch('contreact_ollama.tools.operator_communication.TerminalChannel') as mock_terminal:
        
        # Telegram channel created but send_and_wait times out
        telegram_instance = MagicMock()
        telegram_instance.send_and_wait.side_effect = TimeoutError("No response")
        mock_telegram.return_value = telegram_instance
        
        # Terminal succeeds
        terminal_instance = MagicMock()
        terminal_instance.send_and_wait.return_value = "terminal fallback"
        mock_terminal.return_value = terminal_instance
        
        result = send_message_to_operator("Test", config, "run-001", 5)
        
        # Verify fallback occurred
        assert result == "terminal fallback"


# ===== Context Parameter Tests =====

def test_send_message_with_run_id_and_cycle():
    """Test message sent with run_id and cycle_number context."""
    with patch('contreact_ollama.tools.operator_communication.TerminalChannel') as mock_terminal:
        instance = MagicMock()
        instance.send_and_wait.return_value = "response"
        mock_terminal.return_value = instance
        
        send_message_to_operator("Test", None, "exp-123", 42)
        
        instance.send_and_wait.assert_called_once_with("Test", "exp-123", 42)


def test_send_message_defaults_run_id_and_cycle():
    """Test default values for run_id and cycle_number."""
    with patch('contreact_ollama.tools.operator_communication.TerminalChannel') as mock_terminal:
        instance = MagicMock()
        instance.send_and_wait.return_value = "response"
        mock_terminal.return_value = instance
        
        send_message_to_operator("Test")
        
        # Should use defaults: "unknown" and 0
        instance.send_and_wait.assert_called_once_with("Test", "unknown", 0)


# ===== Edge Cases =====

def test_send_message_handles_empty_input():
    """Test that send_message_to_operator handles empty operator response."""
    with patch('builtins.input', return_value=''):
        result = send_message_to_operator("question")
        assert result == ""


def test_send_message_handles_multiline_message():
    """Test that send_message_to_operator handles messages with newlines."""
    message = "Line 1\nLine 2\nLine 3"
    
    with patch('builtins.input', return_value='response'):
        result = send_message_to_operator(message)
        assert result == "response"


def test_send_message_handles_special_characters():
    """Test that send_message_to_operator handles special characters."""
    message = "Special chars: !@#$%^&*()_+-=[]{}|;':,.<>?/"
    
    with patch('builtins.input', return_value='response'):
        result = send_message_to_operator(message)
        assert result == "response"


def test_send_message_preserves_whitespace():
    """Test that send_message_to_operator preserves whitespace in response."""
    response_with_whitespace = "  response with spaces  "
    
    with patch('builtins.input', return_value=response_with_whitespace):
        result = send_message_to_operator("message")
        assert result == response_with_whitespace


def test_send_message_handles_long_message():
    """Test that send_message_to_operator handles long messages."""
    long_message = "A" * 1000
    
    with patch('builtins.input', return_value='response'):
        result = send_message_to_operator(long_message)
        assert result == "response"
