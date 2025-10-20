"""Unit tests for TerminalChannel."""

from unittest.mock import patch, call
import pytest

from contreact_ollama.communication.terminal_channel import TerminalChannel


def test_terminal_channel_initialization():
    """Test TerminalChannel initializes successfully."""
    channel = TerminalChannel()
    assert channel is not None


def test_send_and_wait_displays_formatted_message(capsys):
    """Test terminal channel formats message with run_id and cycle."""
    channel = TerminalChannel()
    
    with patch("builtins.input", return_value="Test response"):
        response = channel.send_and_wait("Test message", "run-001", 5)
    
    # Verify formatted message was printed
    captured = capsys.readouterr()
    assert "[AGENT - run-001 | Cycle 5]: Test message" in captured.out
    assert response == "Test response"


def test_send_and_wait_returns_operator_input():
    """Test terminal channel returns user input as response."""
    channel = TerminalChannel()
    
    with patch("builtins.input", return_value="Yes, proceed"):
        response = channel.send_and_wait("Continue?", "exp-001", 10)
    
    assert response == "Yes, proceed"


def test_send_and_wait_handles_empty_input():
    """Test terminal channel handles empty operator response."""
    channel = TerminalChannel()
    
    with patch("builtins.input", return_value=""):
        response = channel.send_and_wait("Any input?", "test", 1)
    
    assert response == ""


def test_send_and_wait_handles_multiline_input():
    """Test terminal channel handles multiline responses."""
    channel = TerminalChannel()
    
    multiline_response = "Line 1\nLine 2\nLine 3"
    with patch("builtins.input", return_value=multiline_response):
        response = channel.send_and_wait("Enter text", "test", 1)
    
    assert response == multiline_response


def test_send_and_wait_logs_communication():
    """Test terminal channel logs communication events."""
    channel = TerminalChannel()
    
    with patch("builtins.input", return_value="Test"):
        with patch("contreact_ollama.communication.terminal_channel.logger") as mock_logger:
            response = channel.send_and_wait("Message", "run-001", 3)
            
            # Verify logging calls
            assert mock_logger.info.call_count == 2
            mock_logger.info.assert_any_call(
                "Sending message to operator via terminal (run: run-001, cycle: 3)"
            )
