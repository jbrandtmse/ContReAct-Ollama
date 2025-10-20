"""Operator communication tool for agent-human interaction."""

import logging
from typing import Optional

from contreact_ollama.communication.terminal_channel import TerminalChannel
from contreact_ollama.communication.telegram_channel import TelegramChannel
from contreact_ollama.core.config import ExperimentConfig

logger = logging.getLogger(__name__)


def send_message_to_operator(
    message: str,
    config: Optional[ExperimentConfig] = None,
    run_id: Optional[str] = None,
    cycle_number: Optional[int] = 0
) -> str:
    """
    Send synchronous message to human operator and wait for response.
    
    This function enables bidirectional communication between the agent
    and the human operator during experimental runs. The agent can ask
    questions, provide status updates, or request guidance.
    
    Supports multiple communication channels (terminal, Telegram) based
    on configuration. Automatically falls back to terminal communication
    if Telegram is unavailable or encounters errors.
    
    Args:
        message: The agent's message to display to the operator.
                 This should be a clear, well-formatted question or statement.
        config: Optional experiment configuration for channel selection.
                If None, defaults to terminal communication.
        run_id: Optional run identifier for message context.
                Defaults to "unknown" if not provided.
        cycle_number: Optional cycle number for message context.
                     Defaults to 0 if not provided.
        
    Returns:
        The operator's text response. Returns exactly what the operator types.
        
    Example (backward compatible - no config):
        >>> response = send_message_to_operator("Should I continue with task X?")
        [AGENT]: Should I continue with task X?
        [OPERATOR]: Yes, please proceed
        >>> print(response)
        'Yes, please proceed'
        
    Example (with config - terminal mode):
        >>> config = ExperimentConfig(run_id="exp-001", ..., telegram_enabled=False)
        >>> response = send_message_to_operator("Continue?", config, "exp-001", 5)
        [AGENT - exp-001 | Cycle 5]: Continue?
        [OPERATOR]: Yes
        >>> print(response)
        'Yes'
        
    Example (with config - Telegram mode):
        >>> config = ExperimentConfig(
        ...     run_id="exp-001",
        ...     ...,
        ...     telegram_enabled=True,
        ...     telegram_authorized_users=[123456789],
        ...     telegram_timeout_minutes=5
        ... )
        >>> response = send_message_to_operator("Continue?", config, "exp-001", 5)
        🤖 Agent Message (Run: exp-001, Cycle: 5)
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        Continue?
        >>> print(response)
        'Yes'
        
    Note:
        This function blocks execution until the operator provides input.
        When Telegram is enabled but fails, automatically falls back to terminal.
    """
    # Default values for backward compatibility
    effective_run_id = run_id if run_id is not None else "unknown"
    effective_cycle_number = cycle_number if cycle_number is not None else 0
    
    # Channel selection logic
    if config is None or not config.telegram_enabled:
        # Use terminal channel (default/disabled Telegram)
        logger.info("Using TerminalChannel for operator communication")
        channel = TerminalChannel()
        return channel.send_and_wait(message, effective_run_id, effective_cycle_number)
    
    # Telegram is enabled - try Telegram with fallback to terminal
    logger.info("Attempting to use TelegramChannel for operator communication")
    
    try:
        channel = TelegramChannel(
            authorized_users=config.telegram_authorized_users,
            timeout_minutes=config.telegram_timeout_minutes
        )
        
        response = channel.send_and_wait(message, effective_run_id, effective_cycle_number)
        logger.info("Successfully communicated via Telegram")
        return response
        
    except (ConnectionError, TimeoutError) as e:
        # Telegram failed - fall back to terminal
        logger.warning(
            f"Telegram communication failed: {e}. Falling back to terminal communication."
        )
        
        fallback_channel = TerminalChannel()
        response = fallback_channel.send_and_wait(message, effective_run_id, effective_cycle_number)
        logger.info("Successfully communicated via terminal (fallback)")
        return response
