# Backend Architecture

### Module Organization

**Package Structure**:

```
contreact_ollama/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── experiment_runner.py      # ExperimentRunner class
│   ├── cycle_orchestrator.py     # CycleOrchestrator class
│   └── config.py                  # Configuration loading and validation
├── state/
│   ├── __init__.py
│   ├── agent_state.py             # AgentState dataclass
│   └── models.py                  # Other data models
├── llm/
│   ├── __init__.py
│   ├── ollama_interface.py        # OllamaInterface class
│   ├── prompt_assembler.py        # build_prompt function
│   └── response_parser.py         # parse_ollama_response function
├── tools/
│   ├── __init__.py
│   ├── tool_dispatcher.py         # ToolDispatcher class
│   ├── memory_tools.py            # MemoryTools class
│   └── operator_communication.py  # send_message_to_operator function
├── diversity/
│   ├── __init__.py
│   ├── embedding_service.py       # EmbeddingService class
│   └── similarity_monitor.py      # SimilarityMonitor class
├── logging/
│   ├── __init__.py
│   └── jsonl_logger.py            # JsonlLogger class
└── constants.py                   # System prompt and other constants
```

### Data Access Layer

**Memory Database Access**:
- Encapsulated in `MemoryTools` class
- Supports both TinyDB and SQLite backends
- Factory pattern for database selection

```python
def create_memory_tools(db_type: str, db_path: str, run_id: str) -> MemoryTools:
    """Factory function to create appropriate MemoryTools instance."""
    if db_type == "tinydb":
        return TinyDBMemoryTools(db_path, run_id)
    elif db_type == "sqlite":
        return SQLiteMemoryTools(db_path, run_id)
    else:
        raise ValueError(f"Unsupported database type: {db_type}")
```

**Log File Access**:
- Handled by `JsonlLogger` class
- Direct file I/O with append mode
- No caching layer needed

**Configuration Access**:
- YAML files loaded via `pyyaml` library
- Validation in `config.py` module
- Converted to `ExperimentConfig` dataclass

### Authentication Status

**N/A** - This is a local application with no authentication requirements. The Ollama server also runs locally without authentication.

### Key Design Principles

1. **Separation of Concerns**: Each module has a single, well-defined responsibility
2. **Dependency Injection**: Components receive dependencies via constructor
3. **Stateless Utilities**: Prompt assembly and response parsing are pure functions
4. **Interface Abstraction**: OllamaInterface provides clean abstraction over ollama library
5. **Type Hints**: All public functions and methods have complete type annotations
