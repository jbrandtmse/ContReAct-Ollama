"""Unit tests for TelegramChannel."""

from unittest.mock import patch, MagicMock
import pytest

from contreact_ollama.communication.telegram_channel import TelegramChannel


@pytest.fixture
def mock_telegram_service():
    """Provide mocked TelegramOperatorChannel."""
    with patch('contreact_ollama.communication.telegram_channel.TelegramOperatorChannel') as mock:
        instance = MagicMock()
        instance.check_connection.return_value = True
        instance.send_message.return_value = None
        instance.wait_for_response.return_value = "Test response"
        mock.return_value = instance
        yield mock


def test_telegram_channel_initialization_success(mock_telegram_service):
    """Test TelegramChannel initializes successfully with valid config."""
    channel = TelegramChannel([123456789], 5)
    
    # Verify TelegramOperatorChannel was created
    mock_telegram_service.assert_called_once_with(
        authorized_users=[123456789],
        timeout_minutes=5
    )
    
    # Verify connection check was performed
    mock_telegram_service.return_value.check_connection.assert_called_once()


def test_telegram_channel_initialization_connection_check_fails():
    """Test TelegramChannel initialization fails if connection check fails."""
    with patch('contreact_ollama.communication.telegram_channel.TelegramOperatorChannel') as mock:
        instance = MagicMock()
        instance.check_connection.return_value = False
        mock.return_value = instance
        
        with pytest.raises(ConnectionError, match="connection check failed"):
            channel = TelegramChannel([123456789], 5)


def test_telegram_channel_initialization_bot_token_missing():
    """Test TelegramChannel initialization fails if bot token not set."""
    with patch('contreact_ollama.communication.telegram_channel.TelegramOperatorChannel') as mock:
        mock.side_effect = ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
        
        with pytest.raises(ConnectionError, match="initialization failed"):
            channel = TelegramChannel([123456789], 5)


def test_send_and_wait_success_via_telegram(mock_telegram_service):
    """Test Telegram channel successfully sends and receives message."""
    channel = TelegramChannel([123456789], 5)
    
    response = channel.send_and_wait("Test message", "run-001", 5)
    
    # Verify send_message was called
    mock_telegram_service.return_value.send_message.assert_called_once_with(
        "Test message", "run-001", 5
    )
    
    # Verify wait_for_response was called
    mock_telegram_service.return_value.wait_for_response.assert_called_once()
    
    # Verify response
    assert response == "Test response"


def test_send_and_wait_connection_error_raises_exception(mock_telegram_service):
    """Test Telegram channel raises ConnectionError on network failure."""
    channel = TelegramChannel([123456789], 5)
    
    # Mock send_message to raise exception
    mock_telegram_service.return_value.send_message.side_effect = Exception("Network error")
    
    with pytest.raises(ConnectionError, match="Telegram communication failed"):
        channel.send_and_wait("Test message", "run-001", 5)


def test_send_and_wait_timeout_error_propagated(mock_telegram_service):
    """Test Telegram channel propagates TimeoutError."""
    channel = TelegramChannel([123456789], 5)
    
    # Mock wait_for_response to raise TimeoutError
    mock_telegram_service.return_value.wait_for_response.side_effect = TimeoutError(
        "No response received within 5 minutes"
    )
    
    with pytest.raises(TimeoutError, match="No response received"):
        channel.send_and_wait("Test message", "run-001", 5)


def test_send_and_wait_logs_communication(mock_telegram_service):
    """Test Telegram channel logs communication events."""
    with patch('contreact_ollama.communication.telegram_channel.logger') as mock_logger:
        channel = TelegramChannel([123456789], 5)
        response = channel.send_and_wait("Test message", "run-001", 5)
        
        # Verify logging calls
        assert mock_logger.info.call_count >= 2
        mock_logger.info.assert_any_call(
            "Sending message via Telegram (run: run-001, cycle: 5)"
        )


def test_send_and_wait_handles_long_response(mock_telegram_service):
    """Test Telegram channel handles long operator responses."""
    channel = TelegramChannel([123456789], 5)
    
    long_response = "A" * 1000
    mock_telegram_service.return_value.wait_for_response.return_value = long_response
    
    response = channel.send_and_wait("Test", "run-001", 1)
    
    assert response == long_response
    assert len(response) == 1000
