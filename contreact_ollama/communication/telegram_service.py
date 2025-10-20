"""
Telegram bot service for remote operator communication.

This module provides a Telegram-based communication channel that allows
agents to send messages and receive responses from authorized operators
during long-running experiments.
"""

import logging
import os
import time
from typing import List, Optional

from telegram import Bot, Update
from telegram.error import NetworkError, TelegramError

logger = logging.getLogger(__name__)


class TelegramOperatorChannel:
    """
    Telegram-based communication channel for agent-operator interaction.

    This class provides methods to send messages to authorized Telegram users
    and wait for their responses with configurable timeouts. It includes
    connection health checking and user authorization validation.
    """

    def __init__(self, authorized_users: List[int], timeout_minutes: int = 5) -> None:
        """
        Initialize Telegram bot service.

        Args:
            authorized_users: List of Telegram user IDs authorized to respond
            timeout_minutes: Default timeout in minutes for waiting responses.
                           -1 means wait forever.

        Raises:
            ValueError: If TELEGRAM_BOT_TOKEN environment variable is not set
            ConnectionError: If bot initialization fails

        Example:
            >>> channel = TelegramOperatorChannel([123456789], timeout_minutes=5)
        """
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            raise ValueError(
                "TELEGRAM_BOT_TOKEN environment variable is required for Telegram service"
            )

        self.authorized_users = authorized_users
        self.timeout_minutes = timeout_minutes
        self._pending_response: Optional[str] = None
        self._last_update_id: Optional[int] = None

        try:
            self.bot = Bot(token=token)
            logger.info("TelegramOperatorChannel initialized successfully")
        except TelegramError as e:
            logger.error(f"Failed to initialize Telegram bot: {e}")
            raise ConnectionError(f"Failed to initialize Telegram bot: {e}")

    def check_connection(self) -> bool:
        """
        Verify Telegram bot connection health.

        Returns:
            True if connection is healthy, False otherwise

        Example:
            >>> channel = TelegramOperatorChannel([123456789])
            >>> if channel.check_connection():
            ...     print("Connection OK")
        """
        try:
            bot_info = self.bot.get_me()
            logger.info(f"Connection check successful. Bot: {bot_info.first_name}")
            return True
        except (NetworkError, TelegramError) as e:
            logger.error(f"Connection check failed: {e}")
            return False

    def send_message(self, message: str, run_id: str, cycle_number: int) -> None:
        """
        Send message to authorized users with experiment context.

        Args:
            message: The message content to send
            run_id: Experiment run identifier
            cycle_number: Current cycle number in the experiment

        Raises:
            ConnectionError: If message sending fails due to network issues
            RuntimeError: If Telegram API error occurs

        Example:
            >>> channel = TelegramOperatorChannel([123456789])
            >>> channel.send_message(
            ...     "Should I continue?",
            ...     run_id="exp-001",
            ...     cycle_number=5
            ... )
        """
        formatted_message = self._format_message(message, run_id, cycle_number)

        logger.info(f"Sending Telegram message for run {run_id}, cycle {cycle_number}")

        successful_sends = 0
        errors = []

        for user_id in self.authorized_users:
            try:
                self.bot.send_message(chat_id=user_id, text=formatted_message)
                successful_sends += 1
                logger.debug(f"Message sent successfully to user {user_id}")
            except NetworkError as e:
                error_msg = f"Network error sending to user {user_id}: {e}"
                logger.error(error_msg)
                errors.append(error_msg)
            except TelegramError as e:
                error_msg = f"Telegram API error sending to user {user_id}: {e}"
                logger.error(error_msg)
                errors.append(error_msg)

        if successful_sends == 0:
            # No messages sent successfully
            if errors:
                raise ConnectionError(
                    f"Failed to send message to any authorized user. Errors: {'; '.join(errors)}"
                )
            else:
                raise RuntimeError("No authorized users configured")

        logger.info(f"Message sent successfully to {successful_sends} user(s)")

    def wait_for_response(self, timeout_minutes: Optional[int] = None) -> str:
        """
        Wait for operator response via Telegram with timeout.

        Args:
            timeout_minutes: Minutes to wait before timeout. -1 means wait forever.
                           If None, uses instance default.

        Returns:
            Operator's text response.

        Raises:
            TimeoutError: If timeout expires before response received.
            ValueError: If response is from unauthorized user.
            ConnectionError: If Telegram connection fails.

        Example:
            >>> channel = TelegramOperatorChannel([123456789], timeout_minutes=5)
            >>> response = channel.wait_for_response(5)
            'Yes, proceed with task'
        """
        if timeout_minutes is None:
            timeout_minutes = self.timeout_minutes

        logger.info(
            f"Waiting for Telegram response (timeout: {timeout_minutes} minutes)"
        )

        start_time = time.time()
        timeout_seconds = timeout_minutes * 60 if timeout_minutes > 0 else None

        while True:
            try:
                # Get updates from Telegram
                updates = self.bot.get_updates(
                    offset=self._last_update_id + 1 if self._last_update_id else None,
                    timeout=30,
                )

                for update in updates:
                    self._last_update_id = update.update_id

                    if update.message and update.message.text:
                        user_id = update.message.from_user.id

                        if self._validate_user(user_id):
                            response = update.message.text
                            logger.info(
                                f"Received authorized response from user {user_id}"
                            )
                            return response
                        else:
                            logger.warning(
                                f"Rejected message from unauthorized user {user_id}"
                            )

            except NetworkError as e:
                logger.error(f"Network error while waiting for response: {e}")
                raise ConnectionError(
                    f"Telegram connection lost while waiting for response: {e}"
                )
            except TelegramError as e:
                logger.error(f"Telegram API error while waiting for response: {e}")
                raise ConnectionError(f"Telegram API error: {e}")

            # Check timeout
            if timeout_seconds is not None:
                elapsed = time.time() - start_time
                if elapsed > timeout_seconds:
                    logger.warning(
                        f"Timeout waiting for Telegram response after {timeout_minutes} minutes"
                    )
                    raise TimeoutError(
                        f"No response received within {timeout_minutes} minutes"
                    )

            # Small sleep to avoid tight polling loop
            time.sleep(1)

    def _validate_user(self, user_id: int) -> bool:
        """
        Validate if user is authorized to send responses.

        Args:
            user_id: Telegram user ID to validate

        Returns:
            True if user is authorized, False otherwise

        Example:
            >>> channel = TelegramOperatorChannel([123456789])
            >>> channel._validate_user(123456789)
            True
            >>> channel._validate_user(999999999)
            False
        """
        is_authorized = user_id in self.authorized_users
        if not is_authorized:
            logger.debug(f"User {user_id} is not in authorized list")
        return is_authorized

    def _format_message(self, message: str, run_id: str, cycle_number: int) -> str:
        """
        Format message with experiment context.

        Args:
            message: The message content
            run_id: Experiment run identifier
            cycle_number: Current cycle number

        Returns:
            Formatted message string with context header

        Example:
            >>> channel = TelegramOperatorChannel([123456789])
            >>> formatted = channel._format_message(
            ...     "Should I continue?",
            ...     "exp-001",
            ...     5
            ... )
        """
        return (
            f"🤖 Agent Message (Run: {run_id}, Cycle: {cycle_number})\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{message}"
        )
