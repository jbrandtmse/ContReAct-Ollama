"""
Telegram-based operator communication channel.

This module provides a Telegram-based implementation of the OperatorChannel
protocol, wrapping the TelegramOperatorChannel service for remote operator
communication during experiments.
"""

import logging
from typing import List

from contreact_ollama.communication.telegram_service import TelegramOperatorChannel

logger = logging.getLogger(__name__)


class TelegramChannel:
    """
    Telegram-based operator communication channel.
    
    This channel implementation wraps the TelegramOperatorChannel service
    to provide remote communication with authorized operators via Telegram.
    Performs connection health checks on initialization and handles errors
    with appropriate exceptions for fallback mechanisms.
    
    Example:
        >>> channel = TelegramChannel([123456789], timeout_minutes=5)
        >>> response = channel.send_and_wait("Continue?", "run-001", 5)
        'Yes, proceed'
    """
    
    def __init__(self, authorized_users: List[int], timeout_minutes: int) -> None:
        """
        Initialize Telegram communication channel.
        
        Creates and validates connection to the Telegram bot service.
        Performs health check to ensure the bot is reachable before
        allowing the channel to be used.
        
        Args:
            authorized_users: List of Telegram user IDs authorized to respond
            timeout_minutes: Timeout in minutes for waiting for responses.
                           -1 means wait forever.
            
        Raises:
            ConnectionError: If Telegram bot connection check fails
            ValueError: If TELEGRAM_BOT_TOKEN environment variable not set
            
        Example:
            >>> channel = TelegramChannel([123456789], timeout_minutes=5)
        """
        logger.info("Initializing TelegramChannel")
        
        try:
            self._telegram_service = TelegramOperatorChannel(
                authorized_users=authorized_users,
                timeout_minutes=timeout_minutes
            )
        except ValueError as e:
            # TELEGRAM_BOT_TOKEN not set
            logger.error(f"Failed to initialize Telegram service: {e}")
            raise ConnectionError(f"Telegram initialization failed: {e}") from e
        except Exception as e:
            # Other initialization errors
            logger.error(f"Failed to initialize Telegram service: {e}")
            raise ConnectionError(f"Telegram initialization failed: {e}") from e
        
        # Perform connection health check
        if not self._telegram_service.check_connection():
            logger.error("Telegram bot connection check failed")
            raise ConnectionError("Telegram bot connection check failed")
        
        logger.info("TelegramChannel initialized successfully")
    
    def send_and_wait(self, message: str, run_id: str, cycle_number: int) -> str:
        """
        Send message via Telegram and wait for response.
        
        Sends message to all authorized users via Telegram and waits for
        the first response from any authorized user. Includes timeout
        handling based on configured timeout_minutes.
        
        Args:
            message: The message to send to the operator
            run_id: Unique identifier for the experimental run
            cycle_number: Current cycle number in the experiment
            
        Returns:
            The operator's response as a string
            
        Raises:
            ConnectionError: If Telegram communication fails (network errors)
            TimeoutError: If no response received within timeout period
            
        Example:
            >>> channel = TelegramChannel([123456789], timeout_minutes=5)
            >>> response = channel.send_and_wait("Continue?", "run-001", 5)
            'Yes, proceed with the task'
        """
        logger.info(
            f"Sending message via Telegram (run: {run_id}, cycle: {cycle_number})"
        )
        
        try:
            # Send message to authorized users
            self._telegram_service.send_message(message, run_id, cycle_number)
            
            # Wait for response with configured timeout
            response = self._telegram_service.wait_for_response()
            
            logger.info(
                f"Received Telegram response: {response[:50]}{'...' if len(response) > 50 else ''}"
            )
            
            return response
            
        except TimeoutError as e:
            # Timeout waiting for response - re-raise as TimeoutError
            logger.error(f"Timeout waiting for Telegram response: {e}")
            raise
        except Exception as e:
            # Network errors, Telegram API errors, etc. - raise as ConnectionError
            logger.error(f"Telegram communication error: {e}")
            raise ConnectionError(f"Telegram communication failed: {e}") from e
