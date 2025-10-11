"""
Response Parsing Module

Parses LLM responses to determine if they contain tool calls or final reflections.
Handles extraction and processing of reasoning tags per best practices for autonomous agents.
"""

# Standard library imports
import re
from typing import Dict, Tuple, Any, List, Optional


def extract_thinking_content(content: str) -> Optional[str]:
    """
    Extract content from <thinking>...</thinking> tags.
    
    This preserves the reasoning for logging and analysis without
    including it in the context passed to the next cycle.
    
    Args:
        content: Raw content string that may contain thinking tags
        
    Returns:
        Thinking content if present, None otherwise
        
    Example:
        >>> content = "<thinking>My reasoning here</thinking>\\n\\n<list/>"
        >>> extract_thinking_content(content)
        'My reasoning here'
    """
    match = re.search(r'<thinking>(.*?)</thinking>', content, flags=re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def strip_thinking_tags(content: str) -> str:
    """
    Strip <thinking>...</thinking> tags from content.
    
    Following best practices for autonomous agents, thinking tags are:
    - Logged in full for debugging and analysis (done elsewhere)
    - Stripped from reflections to save tokens in context window
    - Can be summarized if needed for continuity
    
    Args:
        content: Raw content string that may contain thinking tags
        
    Returns:
        Content with thinking tags removed
        
    Example:
        >>> content = "<thinking>Internal reasoning</thinking>\\n\\n<list/>"
        >>> strip_thinking_tags(content)
        '<list/>'
    """
    # Remove <thinking>...</thinking> blocks (including newlines within)
    cleaned = re.sub(r'<thinking>.*?</thinking>', '', content, flags=re.DOTALL)
    
    # Clean up extra whitespace left behind
    cleaned = cleaned.strip()
    
    return cleaned


def parse_ollama_response(response: Dict) -> Tuple[str, Any]:
    """
    Parse response from ollama.chat call.
    
    Args:
        response: Response object from Ollama client
                  Expected structure: {"message": {"role": "assistant", "content": "...", "tool_calls": [...]}}
        
    Returns:
        Tuple of (response_type, data) where:
        - response_type: "TOOL_CALL" if tool_calls present, "FINAL_REFLECTION" otherwise
        - data: List of tool_calls dict or content string (with thinking tags stripped)
        
    Note:
        - Full content (with thinking) is logged via LLM_INVOCATION event
        - Thinking is stripped from reflections to reduce context window tokens
        - This follows best practices for autonomous agent reasoning handling
        
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
        # Final reflection - strip thinking tags before returning
        # (Full content with thinking is already logged in LLM_INVOCATION event)
        content = message.get("content", "")
        cleaned_content = strip_thinking_tags(content)
        return ("FINAL_REFLECTION", cleaned_content)
