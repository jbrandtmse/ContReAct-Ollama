"""Unit tests for OperatorChannel protocol conformance."""

import pytest

from contreact_ollama.communication.channel_protocol import OperatorChannel
from contreact_ollama.communication.terminal_channel import TerminalChannel
from contreact_ollama.communication.telegram_channel import TelegramChannel


def test_terminal_channel_conforms_to_protocol():
    """Test that TerminalChannel conforms to OperatorChannel protocol."""
    # TerminalChannel should have send_and_wait method
    assert hasattr(TerminalChannel, "send_and_wait")
    
    # Method should be callable
    channel = TerminalChannel()
    assert callable(getattr(channel, "send_and_wait", None))


def test_telegram_channel_conforms_to_protocol():
    """Test that TelegramChannel conforms to OperatorChannel protocol."""
    # TelegramChannel should have send_and_wait method
    assert hasattr(TelegramChannel, "send_and_wait")
    
    # Note: Can't instantiate TelegramChannel without valid bot token
    # but we can verify the class has the required method
    assert callable(getattr(TelegramChannel, "send_and_wait", None))


def test_protocol_method_signature():
    """Test that protocol defines correct method signature."""
    # OperatorChannel protocol should define send_and_wait
    # This test verifies the protocol exists and is properly defined
    assert hasattr(OperatorChannel, "send_and_wait")
