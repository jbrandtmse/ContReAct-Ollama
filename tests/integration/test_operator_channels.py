"""Integration tests for operator communication channels."""

from unittest.mock import patch, MagicMock
import pytest

from contreact_ollama.core.config import ExperimentConfig
from contreact_ollama.tools.operator_communication import send_message_to_operator


def test_end_to_end_terminal_communication():
    """Test complete terminal communication flow."""
    # Mock input() for terminal
    with patch('builtins.input', return_value='Yes'):
        response = send_message_to_operator("Continue?", None, "run-001", 1)
        assert response == "Yes"


def test_end_to_end_telegram_communication_with_fallback():
    """Test Telegram communication with fallback to terminal."""
    config = ExperimentConfig(
        run_id="test",
        model_name="test",
        cycle_count=1,
        ollama_client_config={"host": "http://localhost:11434"},
        model_options={},
        telegram_enabled=True,
        telegram_authorized_users=[123],
        telegram_timeout_minutes=5
    )
    
    # Mock Telegram to fail, then mock terminal input
    with patch('contreact_ollama.tools.operator_communication.TelegramChannel') as mock_telegram:
        mock_telegram.side_effect = ConnectionError("Bot not reachable")
        
        with patch('builtins.input', return_value='Fallback response'):
            response = send_message_to_operator("Test", config, "run-001", 1)
            assert response == "Fallback response"


def test_config_based_channel_routing():
    """Test channel routing based on configuration."""
    # Test terminal when telegram_enabled=False
    config_terminal = ExperimentConfig(
        run_id="test",
        model_name="test",
        cycle_count=1,
        ollama_client_config={"host": "http://localhost:11434"},
        model_options={},
        telegram_enabled=False
    )
    
    with patch('builtins.input', return_value='Terminal'):
        response = send_message_to_operator("Test", config_terminal, "run-001", 1)
        assert response == "Terminal"
    
    # Test Telegram when telegram_enabled=True
    config_telegram = ExperimentConfig(
        run_id="test",
        model_name="test",
        cycle_count=1,
        ollama_client_config={"host": "http://localhost:11434"},
        model_options={},
        telegram_enabled=True,
        telegram_authorized_users=[123456789],
        telegram_timeout_minutes=5
    )
    
    with patch('contreact_ollama.tools.operator_communication.TelegramChannel') as mock_telegram:
        instance = MagicMock()
        instance.send_and_wait.return_value = "Telegram response"
        mock_telegram.return_value = instance
        
        response = send_message_to_operator("Test", config_telegram, "run-001", 1)
        assert response == "Telegram response"


def test_backward_compatibility_no_breaking_changes():
    """Test that existing code without config still works."""
    # Old-style call without config should still work
    with patch('builtins.input', return_value='Old style works'):
        response = send_message_to_operator("Test message")
        assert response == "Old style works"
