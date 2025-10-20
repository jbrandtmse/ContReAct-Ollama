"""
Communication channel implementations for operator interaction.

This module provides various communication channels for agent-operator
interaction during experiments, including terminal and Telegram-based channels.
"""

from contreact_ollama.communication.telegram_service import TelegramOperatorChannel

__all__ = ["TelegramOperatorChannel"]
