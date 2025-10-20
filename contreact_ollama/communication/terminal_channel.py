"""
Terminal-based operator communication channel.

This module provides a terminal/console-based implementation of the
OperatorChannel protocol for direct operator interaction via stdin/stdout.
"""

import logging

logger = logging.getLogger(__name__)


class TerminalChannel:
    """
    Terminal-based operator communication channel.
    
    This channel implementation uses standard input/output for synchronous
    communication with the operator. Messages are displayed with context
    (run_id and cycle number) and operator responses are captured via stdin.
    
    This is the default fallback channel when Telegram is disabled or
    unavailable.
    
    Example:
        >>> channel = TerminalChannel()
        >>> response = channel.send_and_wait("Continue?", "run-001", 5)
        [AGENT - run-001 | Cycle 5]: Continue?
        [OPERATOR]: Yes
        'Yes'
    """
    
    def __init__(self) -> None:
        """
        Initialize terminal communication channel.
        
        No configuration required for terminal communication as it uses
        standard input/output streams.
        """
        logger.info("Initialized TerminalChannel")
    
    def send_and_wait(self, message: str, run_id: str, cycle_number: int) -> str:
        """
        Send message to operator via terminal and wait for response.
        
        Displays the message with experiment context to stdout and waits
        for operator input from stdin. The message includes the run_id
        and cycle number for operator context.
        
        Args:
            message: The message to send to the operator
            run_id: Unique identifier for the experimental run
            cycle_number: Current cycle number in the experiment
            
        Returns:
            The operator's response as a string (exactly as typed)
            
        Example:
            >>> channel = TerminalChannel()
            >>> response = channel.send_and_wait("Continue?", "run-001", 5)
            [AGENT - run-001 | Cycle 5]: Continue?
            [OPERATOR]: Yes
            'Yes'
        """
        logger.info(f"Sending message to operator via terminal (run: {run_id}, cycle: {cycle_number})")
        
        # Format message with context
        formatted_message = f"[AGENT - {run_id} | Cycle {cycle_number}]: {message}"
        print(formatted_message)
        
        # Wait for operator response
        response = input("[OPERATOR]: ")
        
        logger.info(f"Received operator response: {response[:50]}{'...' if len(response) > 50 else ''}")
        
        return response
