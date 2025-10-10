"""
Response Parsing Module

Parses LLM responses to determine if they contain tool calls or final reflections.
"""

# Standard library imports
from typing import Dict, Tuple, Any, List


def parse_ollama_response(response: Dict) -> Tuple[str, Any]:
    """
    Parse response from ollama.chat call.
    
    Args:
        response: Response object from Ollama client
                  Expected structure: {"message": {"role": "assistant", "content": "...", "tool_calls": [...]}}
        
    Returns:
        Tuple of (response_type, data) where:
        - response_type: "TOOL_CALL" if tool_calls present, "FINAL_REFLECTION" otherwise
        - data: List of tool_calls dict or content string
        
    Example:
        >>> response = {"message": {"role": "assistant", "tool_calls": [...]}}
        >>> response_type, data = parse_ollama_response(response)
        >>> print(response_type)
        'TOOL_CALL'
    """
    message = response.get("message", {})
    
    # Check for tool calls
    if "tool_calls" in message and message["tool_calls"]:
        return ("TOOL_CALL", message["tool_calls"])
    else:
        # Final reflection
        content = message.get("content", "")
        return ("FINAL_REFLECTION", content)
