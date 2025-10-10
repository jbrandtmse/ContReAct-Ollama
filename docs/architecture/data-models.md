# Data Models

### AgentState

The AgentState is the primary in-memory object representing the agent's condition. It is passed between components and updated throughout each cycle.

**Python Dataclass Definition:**

```python
from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class AgentState:
    """Represents the complete in-memory state of an agent at a point in time."""
    
    run_id: str  # Unique identifier for the experimental run (e.g., 'GPT5-A')
    cycle_number: int  # Current operational cycle number (e.g., 1-10)
    model_name: str  # Tag of the Ollama model being used (e.g., 'llama3:latest')
    message_history: List[Dict[str, Any]] = field(default_factory=list)  # Ordered list of all messages
    reflection_history: List[str] = field(default_factory=list)  # List of final reflection strings
```

**Message History Format:**

Each message in the `message_history` follows the Ollama chat format:

```python
{
    "role": str,  # One of: "system", "user", "assistant", "tool"
    "content": str  # The message content
}
```

### ExperimentConfig

Configuration loaded from YAML files defining experiment parameters.

**Python Dataclass Definition:**

```python
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class ExperimentConfig:
    """Configuration for a single experimental run."""
    
    run_id: str  # Unique identifier for this specific run
    model_name: str  # Model tag as recognized by local Ollama server
    cycle_count: int  # Total number of cycles to run (e.g., 10)
    ollama_client_config: Dict[str, Any]  # Configuration for Ollama client
    model_options: Dict[str, Any]  # Parameters for LLM generation
```

**Model Options Schema:**

```python
{
    "seed": int,  # Random number seed for reproducibility
    "temperature": float,  # Temperature of the model (higher = more creative)
    "top_p": float,  # Works with top_k for nucleus sampling
    "num_predict": int,  # Maximum tokens to generate (-1 = no limit)
    "repeat_last_n": int,  # How far back model looks to prevent repetition
    "repeat_penalty": float,  # How strongly to penalize repetitions
    "num_ctx": int  # Context window size
}
```

### MemoryEntry

Schema for entries in the persistent key-value store.

**Database Table Schema (agent_memory):**

- **run_id** (TEXT, NOT NULL): Unique identifier for the experimental run
- **key** (TEXT, NOT NULL): The key for the memory entry
- **value** (TEXT, NOT NULL): The value associated with the key
- **Primary Key**: (run_id, key)

**TinyDB Document Schema:**

```python
{
    "run_id": str,
    "key": str,
    "value": str
}
```

### LogRecord

Schema for structured log entries written to .jsonl files.

**Python Dataclass Definition:**

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Literal
from enum import Enum

class EventType(Enum):
    """Types of events that can be logged."""
    CYCLE_START = "CYCLE_START"
    LLM_INVOCATION = "LLM_INVOCATION"
    TOOL_CALL = "TOOL_CALL"
    CYCLE_END = "CYCLE_END"

@dataclass
class LogRecord:
    """A single, structured log entry for an experimental event."""
    
    timestamp: str  # ISO 8601 formatted timestamp
    run_id: str  # Identifier for the experiment run
    cycle_number: int  # The cycle in which the event occurred
    event_type: EventType  # The type of event being logged
    payload: Dict[str, Any]  # Event-specific data
```

**Payload Examples by Event Type:**

- **LLM_INVOCATION**: 
  ```python
  {
      "prompt_messages": [...],  # List of messages sent to LLM
      "response_message": {...},  # Response from LLM
      "model_options": {...}  # Generation parameters used
  }
  ```

- **TOOL_CALL**: 
  ```python
  {
      "tool_name": str,  # Name of tool invoked
      "parameters": {...},  # Arguments passed to tool
      "output": str  # Result returned by tool
  }
  ```

- **CYCLE_END**: 
  ```python
  {
      "final_reflection": str,  # Agent's reflection for the cycle
      "metrics": {  # Summary metrics
          "memory_ops_total": int,
          "messages_to_operator": int,
          "response_chars": int,
          "memory_write_chars": int
      }
  }
  ```
