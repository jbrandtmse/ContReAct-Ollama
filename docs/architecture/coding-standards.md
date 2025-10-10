# Coding Standards

### Python Best Practices

This section defines coding standards and conventions for the ContReAct-Ollama project to ensure consistency, maintainability, and readability.

#### 1. Type Hints

**Required**: All public functions, methods, and class attributes must have type hints.

```python
from typing import List, Dict, Optional, Any

def build_prompt(
    agent_state: AgentState, 
    system_prompt: str, 
    tool_definitions: List[Dict[str, Any]], 
    diversity_feedback: Optional[str] = None
) -> List[Dict[str, str]]:
    """Construct the full prompt for LLM invocation."""
    pass
```

**Dataclasses**: Use dataclasses for structured data with type annotations.

```python
from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class AgentState:
    """Represents the complete in-memory state of an agent."""
    run_id: str
    cycle_number: int
    model_name: str
    message_history: List[Dict[str, Any]] = field(default_factory=list)
    reflection_history: List[str] = field(default_factory=list)
```

#### 2. Docstrings

**Required**: All modules, classes, and public functions must have docstrings.

**Format**: Google-style docstrings.

```python
def execute_chat_completion(
    self, 
    model_name: str, 
    messages: List[Dict], 
    tools: List[Dict], 
    options: Dict
) -> Dict:
    """
    Execute LLM chat completion.
    
    Args:
        model_name: Tag of model to use (e.g., 'llama3:latest')
        messages: Message history in Ollama chat format
        tools: Tool definitions in JSON schema format
        options: Generation parameters (temperature, seed, etc.)
        
    Returns:
        Response object from ollama.chat containing message and optional tool_calls
        
    Raises:
        ollama.ResponseError: On connection or model errors
        ValueError: If model_name is empty or invalid
        
    Example:
        >>> interface = OllamaInterface()
        >>> response = interface.execute_chat_completion(
        ...     model_name="llama3:latest",
        ...     messages=[{"role": "user", "content": "Hello"}],
        ...     tools=[],
        ...     options={"temperature": 0.7}
        ... )
    """
    pass
```

#### 3. Code Formatting

**Tool**: Black (line length: 100 characters)

```bash
black --line-length 100 contreact_ollama/
```

**Import Organization**: Use isort with Black-compatible settings.

```python
# Standard library imports
import os
import json
from pathlib import Path
from typing import List, Dict, Optional

# Third-party imports
import ollama
import numpy as np
from tinydb import TinyDB, Query

# Local application imports
from contreact_ollama.state.agent_state import AgentState
from contreact_ollama.core.config import ExperimentConfig
```

#### 4. Naming Conventions

**Classes**: PascalCase
```python
class CycleOrchestrator:
    pass
```

**Functions and Methods**: snake_case
```python
def execute_chat_completion(self, model_name: str) -> Dict:
    pass
```

**Constants**: UPPER_SNAKE_CASE
```python
DEFAULT_TEMPERATURE = 0.7
MAX_RETRIES = 3
SYSTEM_PROMPT = """..."""
```

**Private Methods**: Prefix with underscore
```python
def _load_state(self, cycle_number: int) -> AgentState:
    """Private method for internal use."""
    pass
```

**File Names**: snake_case matching module names
```
cycle_orchestrator.py
experiment_runner.py
ollama_interface.py
```

#### 5. Error Handling

**Specific Exceptions**: Catch specific exceptions, not bare `except`.

```python
# Good
try:
    model_list = self.client.list()
except ollama.ResponseError as e:
    raise ConnectionError(f"Failed to connect to Ollama server: {e}")
except Exception as e:
    raise RuntimeError(f"Unexpected error listing models: {e}")

# Bad
try:
    model_list = self.client.list()
except:  # Never use bare except
    pass
```

**Custom Exceptions**: Define for domain-specific errors.

```python
class ModelNotFoundError(Exception):
    """Raised when required model is not available locally."""
    pass

class InvalidConfigurationError(Exception):
    """Raised when configuration file is invalid or missing required fields."""
    pass
```

#### 6. Function Length and Complexity

**Maximum Length**: Functions should be <50 lines. If longer, refactor into smaller functions.

**Single Responsibility**: Each function should do one thing well.

```python
# Good - Clear single responsibility
def verify_model_availability(self, model_name: str) -> bool:
    """Verify model exists locally."""
    models = self.client.list()
    return any(m['name'] == model_name for m in models)

# Bad - Too many responsibilities
def verify_and_load_model_and_run_experiment(self, config):
    # Verify model
    # Load configuration
    # Initialize services
    # Run experiment
    pass  # This should be split into multiple functions
```

#### 7. Comments

**When to Comment**:
- Complex algorithms requiring explanation
- Non-obvious workarounds
- Important business logic decisions
- TODO items (with ticket number if applicable)

```python
# Calculate cosine similarity using numpy for performance
# This is more efficient than using scipy.spatial for our use case
similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

# TODO(#123): Implement batch embedding generation for better performance
```

**When NOT to Comment**:
- Obvious code that's already clear from naming
- Restating what the code does

```python
# Bad - Comment adds no value
# Increment i by 1
i = i + 1

# Good - No comment needed, code is self-documenting
cycle_number += 1
```

#### 8. Testing Standards

**Coverage**: Aim for >80% code coverage.

**Test Organization**: Mirror source code structure in tests/ directory.

```
contreact_ollama/
└── core/
    └── cycle_orchestrator.py

tests/
└── unit/
    └── test_cycle_orchestrator.py
```

**Test Naming**: `test_<method>_<scenario>_<expected_result>`

```python
def test_verify_model_availability_model_exists_returns_true():
    """Test that verify_model_availability returns True when model exists."""
    pass

def test_execute_chat_completion_connection_error_raises_exception():
    """Test that execute_chat_completion raises exception on connection error."""
    pass
```

**Fixtures**: Use pytest fixtures for common test setup.

```python
import pytest

@pytest.fixture
def sample_config():
    """Provide sample ExperimentConfig for testing."""
    return ExperimentConfig(
        run_id="test-run",
        model_name="llama3:latest",
        cycle_count=10,
        ollama_client_config={"host": "http://localhost:11434"},
        model_options={"temperature": 0.7}
    )
```

#### 9. Logging

**Use Standard Library**: Use Python's `logging` module, not `print()`.

```python
import logging

logger = logging.getLogger(__name__)

def run_experiment(self):
    logger.info(f"Starting experiment: {self.config.run_id}")
    try:
        result = self._execute()
        logger.info(f"Experiment {self.config.run_id} completed successfully")
        return result
    except Exception as e:
        logger.error(f"Experiment failed: {e}", exc_info=True)
        raise
```

**Log Levels**:
- `DEBUG`: Detailed diagnostic information
- `INFO`: General informational messages
- `WARNING`: Warning messages for potentially harmful situations
- `ERROR`: Error messages for failures
- `CRITICAL`: Critical errors causing program termination

#### 10. Code Organization

**Class Structure Order**:
1. Class docstring
2. Class variables
3. `__init__` method
4. Public methods
5. Private methods (prefixed with `_`)
6. Static methods and class methods

```python
class CycleOrchestrator:
    """Manages execution of agent's operational cycles."""
    
    # Class variables
    MAX_CYCLES = 100
    
    def __init__(self, config: ExperimentConfig):
        """Initialize orchestrator with configuration."""
        self.config = config
        
    def run_experiment(self) -> None:
        """Main public method executing full experimental run."""
        pass
        
    def _execute_cycle(self, agent_state: AgentState) -> AgentState:
        """Private method to execute a single cycle."""
        pass
        
    @staticmethod
    def _validate_state(state: AgentState) -> bool:
        """Static helper method for state validation."""
        pass
```

#### 11. Dependencies

**Minimal Dependencies**: Only add dependencies that are absolutely necessary.

**Version Pinning**: Pin major and minor versions in requirements, allow patch updates.

```
# pyproject.toml
ollama>=0.4.0,<0.5.0
sentence-transformers>=3.0.1,<4.0.0
streamlit>=1.38.0,<2.0.0
```

**Import Organization**: Group imports by category, alphabetically within groups.

#### 12. Security Best Practices

**Input Validation**: Always validate external inputs.

```python
def load_config(self, config_path: str) -> ExperimentConfig:
    """Load and validate configuration file."""
    if not Path(config_path).exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
        
    with open(config_path, 'r') as f:
        config_dict = yaml.safe_load(f)  # Use safe_load, not load
        
    # Validate required fields
    required_fields = ['run_id', 'model_name', 'cycle_count']
    for field in required_fields:
        if field not in config_dict:
            raise InvalidConfigurationError(f"Missing required field: {field}")
            
    return ExperimentConfig(**config_dict)
```

**File Paths**: Use Path objects, validate before use.

```python
from pathlib import Path

def ensure_directory(directory: Path) -> None:
    """Ensure directory exists, create if needed."""
    directory = Path(directory).resolve()  # Resolve to absolute path
    directory.mkdir(parents=True, exist_ok=True)
```

### Critical Rules for AI Development Agents

When implementing code based on this architecture:

1. **Follow Type Hints**: All function signatures must match type hints exactly.
2. **Implement Complete Functions**: Never leave placeholder `pass` statements in production code.
3. **Error Handling**: Always handle potential errors with specific exception types.
4. **Test Coverage**: Write unit tests for all new functions and classes.
5. **Docstrings**: Ensure all public APIs are documented with Google-style docstrings.
6. **Code Review**: Run `black`, `isort`, and `mypy` before committing code.
7. **Logging**: Use appropriate log levels, never use `print()` in production code.
8. **Constants**: Define magic numbers and strings as named constants.
