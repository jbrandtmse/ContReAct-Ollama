"""
Prompt Assembly Module

Constructs prompts for LLM invocation by combining system prompt, message history,
and tool definitions.
"""

# Standard library imports
from typing import List, Dict, Any, Optional

# Local application imports
from contreact_ollama.state.agent_state import AgentState


def build_prompt(
    agent_state: AgentState,
    system_prompt: str,
    tool_definitions: List[Dict],
    diversity_feedback: Optional[str] = None
) -> List[Dict[str, str]]:
    """
    Construct the full prompt for LLM invocation.
    
    Args:
        agent_state: Current agent state with message history and reflection history
        system_prompt: Base system prompt text
        tool_definitions: Structured tool definitions in JSON schema format
        diversity_feedback: Optional advisory feedback from SimilarityMonitor
        
    Returns:
        List of message dictionaries formatted for ollama.chat method
        
    Example:
        >>> prompt = build_prompt(agent_state, SYSTEM_PROMPT, tool_defs)
        >>> # Returns: [{"role": "system", "content": "..."}, ...]
    """
    messages = []
    
    # Construct system prompt
    full_system_prompt = system_prompt
    
    # Append reflection history from previous cycles if available
    if agent_state.reflection_history:
        reflection_context = "\n\n## Your Previous Reflections\n"
        reflection_context += "These are your private notes from previous cycles:\n\n"
        for i, reflection in enumerate(agent_state.reflection_history, start=1):
            reflection_context += f"**Cycle {i}**: {reflection}\n\n"
        full_system_prompt += reflection_context
    
    # Append diversity feedback if provided
    if diversity_feedback:
        full_system_prompt += f"\n\n{diversity_feedback}"
    
    # Add system message
    messages.append({
        "role": "system",
        "content": full_system_prompt
    })
    
    # Append existing message history
    messages.extend(agent_state.message_history)
    
    return messages
