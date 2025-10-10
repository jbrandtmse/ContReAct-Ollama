# Standard library imports
from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class AgentState:
    """Represents the complete in-memory state of an agent at a point in time.
    
    This dataclass encapsulates all information needed to track an agent's progress
    through an experimental run, including conversation history and reflections.
    
    Attributes:
        run_id: Unique identifier for the experimental run (e.g., 'GPT5-A')
        cycle_number: Current operational cycle number (e.g., 1-10)
        model_name: Tag of the Ollama model being used (e.g., 'llama3:latest')
        message_history: Ordered list of all messages in Ollama chat format.
            Each message is a dict with 'role' and 'content' keys.
            Roles: 'system', 'user', 'assistant', 'tool'
        reflection_history: List of final reflection strings from each cycle
    """
    
    run_id: str
    cycle_number: int
    model_name: str
    message_history: List[Dict[str, Any]] = field(default_factory=list)
    reflection_history: List[str] = field(default_factory=list)
