"""
Communication channel implementations for operator interaction.

This module provides various communication channels for agent-operator
interaction during experiments, including terminal and Telegram-based channels.
"""

from contreact_ollama.communication.channel_protocol import OperatorChannel
from contreact_ollama.communication.telegram_channel import TelegramChannel
from contreact_ollama.communication.telegram_service import TelegramOperatorChannel
from contreact_ollama.communication.terminal_channel import TerminalChannel

__all__ = [
    "OperatorChannel",
    "TelegramChannel",
    "TelegramOperatorChannel",
    "TerminalChannel",
]
