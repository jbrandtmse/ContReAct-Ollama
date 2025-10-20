"""
Unit tests for Telegram operator communication service.

Tests cover bot initialization, message sending, response waiting,
connection health checks, and error handling scenarios.
"""

import os
import time
from unittest.mock import Mock, MagicMock, patch, PropertyMock

import pytest
from telegram.error import NetworkError, TelegramError

from contreact_ollama.communication.telegram_service import TelegramOperatorChannel


class TestTelegramOperatorChannelInit:
    """Tests for TelegramOperatorChannel initialization."""

    @patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "test_token_123"})
    @patch("contreact_ollama.communication.telegram_service.Bot")
    def test_init_with_valid_token_succeeds(self, mock_bot_class: Mock) -> None:
        """Test TelegramOperatorChannel initialization with valid token."""
        mock_bot_instance = Mock()
        mock_bot_class.return_value = mock_bot_instance

        channel = TelegramOperatorChannel([123456789], timeout_minutes=5)

        assert channel is not None
        assert channel.authorized_users == [123456789]
        assert channel.timeout_minutes == 5
        mock_bot_class.assert_called_once_with(token="test_token_123")

    @patch.dict(os.environ, {}, clear=True)
    def test_init_without_token_raises_valueerror(self) -> None:
        """Test TelegramOperatorChannel initialization fails without token."""
        with pytest.raises(ValueError) as exc_info:
            TelegramOperatorChannel([123456789])

        assert "TELEGRAM_BOT_TOKEN environment variable is required" in str(exc_info.value)

    @patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "test_token_123"})
    @patch("contreact_ollama.communication.telegram_service.Bot")
    def test_init_with_bot_error_raises_connectionerror(self, mock_bot_class: Mock) -> None:
        """Test initialization fails gracefully when Bot raises TelegramError."""
        mock_bot_class.side_effect = TelegramError("Invalid token")

        with pytest.raises(ConnectionError) as exc_info:
            TelegramOperatorChannel([123456789])

        assert "Failed to initialize Telegram bot" in str(exc_info.value)


class TestCheckConnection:
    """Tests for connection health check."""

    @patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "test_token_123"})
    @patch("contreact_ollama.communication.telegram_service.Bot")
    def test_check_connection_success_returns_true(self, mock_bot_class: Mock) -> None:
        """Test check_connection returns True when bot is reachable."""
        mock_bot = Mock()
        mock_bot.get_me.return_value = Mock(first_name="TestBot", id=123)
        mock_bot_class.return_value = mock_bot

        channel = TelegramOperatorChannel([123456789])
        result = channel.check_connection()

        assert result is True
        mock_bot.get_me.assert_called_once()

    @patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "test_token_123"})
    @patch("contreact_ollama.communication.telegram_service.Bot")
    def test_check_connection_network_error_returns_false(self, mock_bot_class: Mock) -> None:
        """Test check_connection returns False on NetworkError."""
        mock_bot = Mock()
        mock_bot.get_me.side_effect = NetworkError("Connection timeout")
        mock_bot_class.return_value = mock_bot

        channel = TelegramOperatorChannel([123456789])
        result = channel.check_connection()

        assert result is False

    @patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "test_token_123"})
    @patch("contreact_ollama.communication.telegram_service.Bot")
    def test_check_connection_telegram_error_returns_false(self, mock_bot_class: Mock) -> None:
        """Test check_connection returns False on TelegramError."""
        mock_bot = Mock()
        mock_bot.get_me.side_effect = TelegramError("API error")
        mock_bot_class.return_value = mock_bot

        channel = TelegramOperatorChannel([123456789])
        result = channel.check_connection()

        assert result is False


class TestSendMessage:
    """Tests for sending messages to Telegram."""

    @patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "test_token_123"})
    @patch("contreact_ollama.communication.telegram_service.Bot")
    def test_send_message_success_sends_to_all_users(self, mock_bot_class: Mock) -> None:
        """Test send_message successfully sends to all authorized users."""
        mock_bot = Mock()
        mock_bot_class.return_value = mock_bot

        channel = TelegramOperatorChannel([123456789, 987654321])
        channel.send_message("Test message", run_id="exp-001", cycle_number=5)

        assert mock_bot.send_message.call_count == 2
        calls = mock_bot.send_message.call_args_list
        assert calls[0][1]["chat_id"] == 123456789
        assert calls[1][1]["chat_id"] == 987654321
        assert "Test message" in calls[0][1]["text"]
        assert "exp-001" in calls[0][1]["text"]
        assert "Cycle: 5" in calls[0][1]["text"]

    @patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "test_token_123"})
    @patch("contreact_ollama.communication.telegram_service.Bot")
    def test_send_message_network_error_raises_connectionerror(
        self, mock_bot_class: Mock
    ) -> None:
        """Test send_message raises ConnectionError on NetworkError."""
        mock_bot = Mock()
        mock_bot.send_message.side_effect = NetworkError("Connection lost")
        mock_bot_class.return_value = mock_bot

        channel = TelegramOperatorChannel([123456789])

        with pytest.raises(ConnectionError) as exc_info:
            channel.send_message("Test", run_id="exp-001", cycle_number=1)

        assert "Failed to send message to any authorized user" in str(exc_info.value)

    @patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "test_token_123"})
    @patch("contreact_ollama.communication.telegram_service.Bot")
    def test_send_message_telegram_error_raises_connectionerror(
        self, mock_bot_class: Mock
    ) -> None:
        """Test send_message raises ConnectionError on TelegramError."""
        mock_bot = Mock()
        mock_bot.send_message.side_effect = TelegramError("API error")
        mock_bot_class.return_value = mock_bot

        channel = TelegramOperatorChannel([123456789])

        with pytest.raises(ConnectionError) as exc_info:
            channel.send_message("Test", run_id="exp-001", cycle_number=1)

        assert "Failed to send message to any authorized user" in str(exc_info.value)

    @patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "test_token_123"})
    @patch("contreact_ollama.communication.telegram_service.Bot")
    def test_send_message_no_authorized_users_raises_runtimeerror(
        self, mock_bot_class: Mock
    ) -> None:
        """Test send_message raises RuntimeError when no authorized users."""
        mock_bot = Mock()
        mock_bot_class.return_value = mock_bot

        channel = TelegramOperatorChannel([])

        with pytest.raises(RuntimeError) as exc_info:
            channel.send_message("Test", run_id="exp-001", cycle_number=1)

        assert "No authorized users configured" in str(exc_info.value)

    @patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "test_token_123"})
    @patch("contreact_ollama.communication.telegram_service.Bot")
    def test_send_message_partial_success_succeeds(self, mock_bot_class: Mock) -> None:
        """Test send_message succeeds if at least one user receives message."""
        mock_bot = Mock()

        def send_side_effect(chat_id: int, text: str) -> None:
            if chat_id == 123456789:
                return  # Success
            else:
                raise NetworkError("Failed")

        mock_bot.send_message.side_effect = send_side_effect
        mock_bot_class.return_value = mock_bot

        channel = TelegramOperatorChannel([123456789, 987654321])
        # Should not raise since one message succeeded
        channel.send_message("Test", run_id="exp-001", cycle_number=1)

        assert mock_bot.send_message.call_count == 2


class TestWaitForResponse:
    """Tests for waiting for operator responses."""

    @patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "test_token_123"})
    @patch("contreact_ollama.communication.telegram_service.Bot")
    def test_wait_for_response_authorized_user_returns_message(
        self, mock_bot_class: Mock
    ) -> None:
        """Test wait_for_response returns message from authorized user."""
        mock_bot = Mock()
        mock_update = Mock()
        mock_update.update_id = 1
        mock_update.message.text = "Yes, proceed"
        mock_update.message.from_user.id = 123456789

        mock_bot.get_updates.return_value = [mock_update]
        mock_bot_class.return_value = mock_bot

        channel = TelegramOperatorChannel([123456789], timeout_minutes=1)
        response = channel.wait_for_response(timeout_minutes=1)

        assert response == "Yes, proceed"

    @patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "test_token_123"})
    @patch("contreact_ollama.communication.telegram_service.Bot")
    def test_wait_for_response_unauthorized_user_rejects_message(
        self, mock_bot_class: Mock
    ) -> None:
        """Test wait_for_response rejects messages from unauthorized users."""
        mock_bot = Mock()

        # First update from unauthorized user
        mock_update1 = Mock()
        mock_update1.update_id = 1
        mock_update1.message.text = "Unauthorized message"
        mock_update1.message.from_user.id = 999999999

        # Second update from authorized user
        mock_update2 = Mock()
        mock_update2.update_id = 2
        mock_update2.message.text = "Authorized message"
        mock_update2.message.from_user.id = 123456789

        mock_bot.get_updates.side_effect = [[mock_update1], [mock_update2]]
        mock_bot_class.return_value = mock_bot

        channel = TelegramOperatorChannel([123456789], timeout_minutes=1)
        response = channel.wait_for_response(timeout_minutes=1)

        # Should return authorized message, not unauthorized one
        assert response == "Authorized message"

    @patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "test_token_123"})
    @patch("contreact_ollama.communication.telegram_service.Bot")
    @patch("contreact_ollama.communication.telegram_service.time")
    def test_wait_for_response_timeout_raises_timeouterror(
        self, mock_time: Mock, mock_bot_class: Mock
    ) -> None:
        """Test wait_for_response raises TimeoutError after timeout expires."""
        mock_bot = Mock()
        mock_bot.get_updates.return_value = []  # No updates
        mock_bot_class.return_value = mock_bot

        # Mock time to simulate timeout
        mock_time.time.side_effect = [0, 0, 0, 0, 400]  # Exceeds 5 minutes (300 seconds)
        mock_time.sleep.return_value = None

        channel = TelegramOperatorChannel([123456789], timeout_minutes=5)

        with pytest.raises(TimeoutError) as exc_info:
            channel.wait_for_response(timeout_minutes=5)

        assert "No response received within 5 minutes" in str(exc_info.value)

    @patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "test_token_123"})
    @patch("contreact_ollama.communication.telegram_service.Bot")
    def test_wait_for_response_network_error_raises_connectionerror(
        self, mock_bot_class: Mock
    ) -> None:
        """Test wait_for_response raises ConnectionError on NetworkError."""
        mock_bot = Mock()
        mock_bot.get_updates.side_effect = NetworkError("Connection lost")
        mock_bot_class.return_value = mock_bot

        channel = TelegramOperatorChannel([123456789], timeout_minutes=1)

        with pytest.raises(ConnectionError) as exc_info:
            channel.wait_for_response(timeout_minutes=1)

        assert "Telegram connection lost" in str(exc_info.value)

    @patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "test_token_123"})
    @patch("contreact_ollama.communication.telegram_service.Bot")
    def test_wait_for_response_telegram_error_raises_connectionerror(
        self, mock_bot_class: Mock
    ) -> None:
        """Test wait_for_response raises ConnectionError on TelegramError."""
        mock_bot = Mock()
        mock_bot.get_updates.side_effect = TelegramError("API error")
        mock_bot_class.return_value = mock_bot

        channel = TelegramOperatorChannel([123456789], timeout_minutes=1)

        with pytest.raises(ConnectionError) as exc_info:
            channel.wait_for_response(timeout_minutes=1)

        assert "Telegram API error" in str(exc_info.value)

    @patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "test_token_123"})
    @patch("contreact_ollama.communication.telegram_service.Bot")
    def test_wait_for_response_uses_instance_timeout_when_none(
        self, mock_bot_class: Mock
    ) -> None:
        """Test wait_for_response uses instance timeout when parameter is None."""
        mock_bot = Mock()
        mock_update = Mock()
        mock_update.update_id = 1
        mock_update.message.text = "Response"
        mock_update.message.from_user.id = 123456789

        mock_bot.get_updates.return_value = [mock_update]
        mock_bot_class.return_value = mock_bot

        channel = TelegramOperatorChannel([123456789], timeout_minutes=10)
        response = channel.wait_for_response(timeout_minutes=None)

        assert response == "Response"


class TestValidateUser:
    """Tests for user authorization validation."""

    @patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "test_token_123"})
    @patch("contreact_ollama.communication.telegram_service.Bot")
    def test_validate_user_authorized_returns_true(self, mock_bot_class: Mock) -> None:
        """Test _validate_user returns True for authorized user."""
        mock_bot_class.return_value = Mock()

        channel = TelegramOperatorChannel([123456789, 987654321])
        result = channel._validate_user(123456789)

        assert result is True

    @patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "test_token_123"})
    @patch("contreact_ollama.communication.telegram_service.Bot")
    def test_validate_user_unauthorized_returns_false(self, mock_bot_class: Mock) -> None:
        """Test _validate_user returns False for unauthorized user."""
        mock_bot_class.return_value = Mock()

        channel = TelegramOperatorChannel([123456789])
        result = channel._validate_user(999999999)

        assert result is False


class TestFormatMessage:
    """Tests for message formatting."""

    @patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "test_token_123"})
    @patch("contreact_ollama.communication.telegram_service.Bot")
    def test_format_message_includes_context(self, mock_bot_class: Mock) -> None:
        """Test _format_message includes run_id and cycle_number."""
        mock_bot_class.return_value = Mock()

        channel = TelegramOperatorChannel([123456789])
        formatted = channel._format_message("Test message", "exp-001", 5)

        assert "exp-001" in formatted
        assert "Cycle: 5" in formatted
        assert "Test message" in formatted
        assert "🤖" in formatted  # Bot emoji
        assert "━" in formatted  # Separator line
