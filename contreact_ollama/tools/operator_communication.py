"""Operator communication tool for agent-human interaction."""


def send_message_to_operator(message: str) -> str:
    """
    Send synchronous message to human operator and wait for response.
    
    This function enables bidirectional communication between the agent
    and the human operator during experimental runs. The agent can ask
    questions, provide status updates, or request guidance.
    
    Args:
        message: The agent's message to display to the operator.
                 This should be a clear, well-formatted question or statement.
        
    Returns:
        The operator's text response. Returns exactly what the operator types.
        
    Example:
        >>> response = send_message_to_operator("Should I continue with task X?")
        [AGENT]: Should I continue with task X?
        [OPERATOR]: Yes, please proceed
        >>> print(response)
        'Yes, please proceed'
        
    Note:
        This function blocks execution until the operator provides input.
        The console output uses [AGENT]: and [OPERATOR]: prefixes for clarity.
    """
    print(f"[AGENT]: {message}")
    response = input("[OPERATOR]: ")
    return response
