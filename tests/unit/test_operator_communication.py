"""Unit tests for operator communication tool."""

# Standard library imports
from unittest.mock import patch, call

# Third-party imports
import pytest

# Local application imports
from contreact_ollama.tools.operator_communication import send_message_to_operator


def test_send_message_prints_agent_prefix():
    """Test that send_message_to_operator prints message with [AGENT]: prefix."""
    with patch('builtins.print') as mock_print, \
         patch('builtins.input', return_value='operator response'):
        
        send_message_to_operator("What should I do?")
        
        # Verify print called with agent prefix
        mock_print.assert_called_once_with("[AGENT]: What should I do?")


def test_send_message_prompts_operator():
    """Test that send_message_to_operator prompts operator with [OPERATOR]: prefix."""
    with patch('builtins.print'), \
         patch('builtins.input', return_value='test response') as mock_input:
        
        send_message_to_operator("question")
        
        # Verify input called with operator prompt
        mock_input.assert_called_once_with("[OPERATOR]: ")


def test_send_message_returns_operator_input():
    """Test that send_message_to_operator returns operator's response."""
    with patch('builtins.print'), \
         patch('builtins.input', return_value='operator response'):
        
        result = send_message_to_operator("message")
        
        # Verify operator's response returned
        assert result == "operator response"


def test_send_message_handles_empty_input():
    """Test that send_message_to_operator handles empty operator response."""
    with patch('builtins.print'), \
         patch('builtins.input', return_value=''):
        
        result = send_message_to_operator("question")
        
        # Verify empty string returned (valid response)
        assert result == ""


def test_send_message_handles_multiline_message():
    """Test that send_message_to_operator handles messages with newlines."""
    message = "Line 1\nLine 2\nLine 3"
    
    with patch('builtins.print') as mock_print, \
         patch('builtins.input', return_value='response'):
        
        result = send_message_to_operator(message)
        
        # Verify message printed correctly
        mock_print.assert_called_once_with(f"[AGENT]: {message}")
        assert result == "response"


def test_send_message_handles_special_characters():
    """Test that send_message_to_operator handles special characters."""
    message = "Special chars: !@#$%^&*()_+-=[]{}|;':,.<>?/"
    response = "Response with special chars: !@#$%"
    
    with patch('builtins.print') as mock_print, \
         patch('builtins.input', return_value=response):
        
        result = send_message_to_operator(message)
        
        # Verify special characters handled correctly
        mock_print.assert_called_once_with(f"[AGENT]: {message}")
        assert result == response


def test_send_message_complete_interaction():
    """Test complete interaction flow from agent to operator."""
    with patch('builtins.print') as mock_print, \
         patch('builtins.input', return_value='Yes, please proceed') as mock_input:
        
        result = send_message_to_operator("Should I continue with task X?")
        
        # Verify print called with agent prefix
        mock_print.assert_called_once_with("[AGENT]: Should I continue with task X?")
        
        # Verify input called with operator prompt
        mock_input.assert_called_once_with("[OPERATOR]: ")
        
        # Verify operator's response returned
        assert result == "Yes, please proceed"


def test_send_message_preserves_whitespace():
    """Test that send_message_to_operator preserves whitespace in response."""
    response_with_whitespace = "  response with spaces  "
    
    with patch('builtins.print'), \
         patch('builtins.input', return_value=response_with_whitespace):
        
        result = send_message_to_operator("message")
        
        # Verify whitespace preserved
        assert result == response_with_whitespace


def test_send_message_handles_long_message():
    """Test that send_message_to_operator handles long messages."""
    long_message = "A" * 1000  # 1000 character message
    
    with patch('builtins.print') as mock_print, \
         patch('builtins.input', return_value='response'):
        
        result = send_message_to_operator(long_message)
        
        # Verify long message printed correctly
        mock_print.assert_called_once_with(f"[AGENT]: {long_message}")
        assert result == "response"
