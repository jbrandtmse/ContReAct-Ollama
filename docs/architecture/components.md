# Components

### 1. ExperimentRunner

**Purpose**: Top-level component and main entry point for the application.

**Responsibilities**:
- Parse experiment configuration from YAML file
- Initialize all service components
- Launch experimental runs
- Handle top-level error reporting

**Key Methods**:

```python
class ExperimentRunner:
    def __init__(self, config_path: str):
        """Initialize runner with path to configuration file."""
        
    def load_config(self) -> ExperimentConfig:
        """Load and validate YAML configuration file."""
        
    def initialize_services(self) -> dict:
        """Initialize all required services (Ollama, Logger, Tools, etc.)."""
        
    def run(self) -> None:
        """Execute the complete experimental run."""
```

### 2. CycleOrchestrator

**Purpose**: The heart of the system that manages execution of agent's operational cycles.

**Responsibilities**:
- Manage state machine transitions
- Direct control flow between states
- Determine when experimental run is complete
- Coordinate between all other components

**Key Methods**:

```python
class CycleOrchestrator:
    def __init__(self, config: ExperimentConfig, ollama_interface: OllamaInterface,
                 tool_dispatcher: ToolDispatcher, logger: JsonlLogger, 
                 similarity_monitor: SimilarityMonitor):
        """Initialize orchestrator with all necessary services."""
        
    def run_experiment(self) -> None:
        """Main public method executing full experimental run from Cycle 1 to cycle_count."""
        
    def _execute_cycle(self, agent_state: AgentState) -> AgentState:
        """Execute a single cycle of the ContReAct state machine."""
        
    def _load_state(self, cycle_number: int) -> AgentState:
        """LOAD_STATE: Load or initialize AgentState."""
        
    def _assemble_prompt(self, agent_state: AgentState) -> List[Dict]:
        """ASSEMBLE_PROMPT: Construct full context for LLM."""
        
    def _invoke_llm(self, messages: List[Dict]) -> Dict:
        """INVOKE_LLM: Send prompt to Ollama server."""
        
    def _parse_response(self, response: Dict) -> Tuple[str, Any]:
        """PARSE_RESPONSE: Determine if response contains tool calls or final reflection."""
        
    def _dispatch_tool(self, tool_call: Dict, agent_state: AgentState) -> str:
        """DISPATCH_TOOL: Invoke tool and return result."""
        
    def _finalize_cycle(self, agent_state: AgentState, reflection: str) -> None:
        """FINALIZE_CYCLE: Extract reflection, calculate embedding, log state."""
        
    def _should_terminate(self, cycle_number: int) -> bool:
        """TERMINATE_OR_CONTINUE: Check if target cycle count reached."""
```

### 3. PromptAssembler

**Purpose**: Stateless utility module for constructing LLM inputs.

**Responsibilities**:
- Build complete prompt with all required components
- Format messages according to Ollama chat format
- Append diversity feedback when applicable

**Key Function**:

```python
def build_prompt(agent_state: AgentState, system_prompt: str, 
                 tool_definitions: List[Dict], 
                 diversity_feedback: Optional[str] = None) -> List[Dict[str, str]]:
    """
    Construct the full prompt for LLM invocation.
    
    Args:
        agent_state: Current agent state with message history
        system_prompt: Base system prompt text
        tool_definitions: Structured tool definitions in JSON schema format
        diversity_feedback: Optional advisory feedback from SimilarityMonitor
        
    Returns:
        List of message dictionaries formatted for ollama.chat method
    """
```

### 4. ResponseParser

**Purpose**: Stateless utility module for interpreting Ollama responses.

**Responsibilities**:
- Check for presence of tool calls
- Validate tool call structure
- Extract final reflections
- Determine response type

**Key Function**:

```python
def parse_ollama_response(response: Dict) -> Tuple[str, Any]:
    """
    Parse response from ollama.chat call.
    
    Args:
        response: Response object from Ollama client
        
    Returns:
        Tuple of (response_type, data) where:
        - response_type: "TOOL_CALL" or "FINAL_REFLECTION"
        - data: List of tool calls or reflection string
    """
```

### 5. OllamaInterface

**Purpose**: Wrapper around ollama Python library for all LLM communication.

**Responsibilities**:
- Initialize ollama.Client with host configuration
- Verify model availability before experiments
- Execute chat completions with proper parameters
- Handle API-level errors with clear feedback

**Key Methods**:

```python
class OllamaInterface:
    def __init__(self, host: str = "http://localhost:11434"):
        """Initialize Ollama client with specified host."""
        self.client = ollama.Client(host=host)
        
    def verify_model_availability(self, model_name: str) -> bool:
        """
        Verify model exists locally.
        
        Calls ollama.list() and checks if model_name is present.
        Raises error with instructions to run 'ollama pull' if not found.
        """
        
    def execute_chat_completion(self, model_name: str, messages: List[Dict], 
                                tools: List[Dict], options: Dict) -> Dict:
        """
        Execute LLM chat completion.
        
        Args:
            model_name: Tag of model to use
            messages: Message history
            tools: Tool definitions in JSON schema format
            options: Generation parameters (temperature, seed, etc.)
            
        Returns:
            Response object from ollama.chat
            
        Raises:
            ollama.ResponseError: On connection or model errors
        """
```

### 6. ToolDispatcher

**Purpose**: Manage and invoke the suite of tools available to the agent.

**Responsibilities**:
- Maintain registry of available tools
- Route tool calls to appropriate functions
- Format tool results as messages
- Track tool usage for logging

**Key Methods**:

```python
class ToolDispatcher:
    def __init__(self, memory_tools: MemoryTools):
        """Initialize with memory tools instance."""
        self.tools = {
            "write": memory_tools.write,
            "read": memory_tools.read,
            "list": memory_tools.list,
            "delete": memory_tools.delete,
            "pattern_search": memory_tools.pattern_search,
            "send_message_to_operator": send_message_to_operator
        }
        
    def dispatch(self, tool_name: str, arguments: Dict) -> str:
        """
        Invoke requested tool with arguments.
        
        Args:
            tool_name: Name of tool to invoke
            arguments: Dictionary of arguments for the tool
            
        Returns:
            String result from tool execution
        """
        
    def get_tool_definitions(self) -> List[Dict]:
        """Generate JSON schema definitions for all available tools."""
```

### 7. MemoryTools

**Purpose**: Encapsulate all persistent memory operations.

**Responsibilities**:
- Provide CRUD operations on key-value store
- Support pattern-based searching
- Ensure multi-tenant isolation by run_id

**Key Methods**:

```python
class MemoryTools:
    def __init__(self, db_path: str, run_id: str):
        """Initialize with path to database file and current run_id."""
        
    def write(self, key: str, value: str) -> str:
        """
        Write value to specified key in persistent memory.
        Overwrites if key exists.
        Returns confirmation message.
        """
        
    def read(self, key: str) -> str:
        """
        Read value associated with specified key.
        Returns value or error if key not found.
        """
        
    def list(self) -> str:
        """
        List all keys currently stored.
        Returns comma-separated string of keys.
        """
        
    def delete(self, key: str) -> str:
        """
        Delete key and its associated value.
        Returns confirmation message.
        """
        
    def pattern_search(self, pattern: str) -> str:
        """
        Search for keys containing the given pattern string.
        Returns comma-separated string of matching keys.
        """
```

### 8. Operator Communication Tool

**Purpose**: Enable synchronous communication between agent and human operator.

**Implementation**:

```python
def send_message_to_operator(message: str) -> str:
    """
    Send synchronous message to human operator and wait for response.
    
    Args:
        message: The agent's message to the operator
        
    Returns:
        The operator's text response
        
    Implementation:
        - Print message to console with [AGENT]: prefix
        - Block and wait for operator input with [OPERATOR]: prompt
        - Return operator's entered text
    """
    print(f"[AGENT]: {message}")
    response = input("[OPERATOR]: ")
    return response
```

### 9. JsonlLogger

**Purpose**: Centralized logging service for all experimental events.

**Responsibilities**:
- Write structured log records to .jsonl file
- Ensure proper formatting and file locking
- Generate ISO 8601 timestamps
- Support concurrent writes (if needed)

**Key Methods**:

```python
class JsonlLogger:
    def __init__(self, log_file_path: str):
        """
        Initialize logger with output file path.
        Opens file in append mode.
        """
        
    def log_event(self, run_id: str, cycle_number: int, 
                  event_type: EventType, payload: Dict) -> None:
        """
        Log a single event to the file.
        
        Args:
            run_id: Experiment run identifier
            cycle_number: Current cycle number
            event_type: Type of event (CYCLE_START, LLM_INVOCATION, etc.)
            payload: Event-specific data
            
        Implementation:
            - Create LogRecord with current timestamp
            - Serialize to JSON string
            - Write line to file with newline
        """
```

### 10. EmbeddingService

**Purpose**: Generate semantic embeddings for text using sentence-transformers.

**Responsibilities**:
- Load and manage sentence transformer model
- Convert text to embedding vectors
- Provide consistent embedding dimensions

**Key Methods**:

```python
class EmbeddingService:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize with specified sentence transformer model.
        Default: all-MiniLM-L6-v2 (384-dimensional embeddings)
        """
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)
        
    def get_embedding(self, text: str) -> numpy.ndarray:
        """
        Convert text to embedding vector.
        
        Args:
            text: Input text (agent's reflection)
            
        Returns:
            384-dimensional numpy array embedding vector
        """
```

### 11. SimilarityMonitor

**Purpose**: Track reflection similarity and generate advisory feedback.

**Responsibilities**:
- Calculate cosine similarity between embeddings
- Apply threshold-based feedback rules
- Generate appropriate advisory messages

**Key Methods**:

```python
class SimilarityMonitor:
    def __init__(self, embedding_service: EmbeddingService):
        """Initialize with embedding service instance."""
        
    def check_similarity(self, new_reflection_embedding: numpy.ndarray, 
                        historical_embeddings: List[numpy.ndarray]) -> Optional[str]:
        """
        Check similarity of new reflection against historical reflections.
        
        Args:
            new_reflection_embedding: Embedding of latest reflection
            historical_embeddings: List of all previous reflection embeddings
            
        Returns:
            Advisory feedback string if similarity exceeds threshold, None otherwise
            
        Thresholds:
            - > 0.8: "Advisory: Your current line of reflection shows high similarity..."
            - > 0.7: "Advisory: Your current line of reflection shows moderate similarity..."
            - <= 0.7: No feedback (returns None)
        """
```

### 12. Web UI Components (Streamlit)

**Dashboard Entry Point** (`dashboard.py`):
- Initializes Streamlit app
- Configures page layout and theme
- Serves as router for multi-page app

**Configuration Page** (`pages/1_🧪_Experiment_Configuration.py`):
- Form for creating/editing config.yaml files
- Dropdown for loading existing configurations
- Save functionality to configs/ directory

**Results Dashboard** (`pages/2_📊_Results_Dashboard.py`):
- Run selector dropdown (scans logs/ directory)
- Metrics display using st.metric and st.dataframe
- Interactive Plotly charts
- Expandable raw log viewer
- PEI assessment results display (if available)
