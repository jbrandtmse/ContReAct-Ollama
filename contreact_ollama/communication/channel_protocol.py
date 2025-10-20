"""
Protocol definition for operator communication channels.

This module defines the OperatorChannel protocol that all communication
channel implementations must conform to, enabling polymorphic channel
selection at runtime.
"""

from typing import Protocol


class OperatorChannel(Protocol):
    """
    Protocol defining interface for operator communication channels.
    
    All communication channel implementations (Terminal, Telegram, etc.)
    must implement this protocol to ensure consistent behavior across
    different communication methods.
    
    Example:
        >>> class MyChannel:
        ...     def send_and_wait(self, message: str, run_id: str, cycle_number: int) -> str:
        ...         # Implementation here
        ...         pass
        >>> channel: OperatorChannel = MyChannel()
    """
    
    def send_and_wait(self, message: str, run_id: str, cycle_number: int) -> str:
        """
        Send message to operator and wait for response.
        
        This method combines sending a message and waiting for a response
        into a single atomic operation, ensuring the channel implementation
        handles the complete communication flow.
        
        Args:
            message: The message to send to the operator. Should be clear
                    and provide sufficient context for the operator.
            run_id: Unique identifier for the experimental run. Used for
                   message formatting and logging context.
            cycle_number: Current cycle number in the experiment. Provides
                         temporal context for the operator.
            
        Returns:
            The operator's response as a string. The response should be
            the raw text provided by the operator without modification.
            
        Raises:
            ConnectionError: If communication channel fails or becomes
                           unavailable during the operation.
            TimeoutError: If no response is received within the configured
                        timeout period (channel-specific).
            
        Example:
            >>> channel = SomeChannel()
            >>> response = channel.send_and_wait(
            ...     "Should I continue?",
            ...     run_id="exp-001",
            ...     cycle_number=5
            ... )
            >>> print(response)
            'Yes, proceed with the task'
        """
        ...
