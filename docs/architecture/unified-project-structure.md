# Unified Project Structure

Complete directory tree for the monorepo:

```
contreact-ollama/
├── .gitignore
├── README.md
├── LICENSE
├── pyproject.toml                 # Project metadata and dependencies
├── setup.py                        # Package installation script
│
├── contreact_ollama/               # Main Python package
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── experiment_runner.py
│   │   ├── cycle_orchestrator.py
│   │   └── config.py
│   ├── state/
│   │   ├── __init__.py
│   │   ├── agent_state.py
│   │   └── models.py
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── ollama_interface.py
│   │   ├── prompt_assembler.py
│   │   └── response_parser.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── tool_dispatcher.py
│   │   ├── memory_tools.py
│   │   └── operator_communication.py
│   ├── diversity/
│   │   ├── __init__.py
│   │   ├── embedding_service.py
│   │   └── similarity_monitor.py
│   ├── logging/
│   │   ├── __init__.py
│   │   └── jsonl_logger.py
│   └── constants.py
│
├── ui/                             # Streamlit web interface
│   ├── dashboard.py                # Main entry point
│   └── pages/
│       ├── 1_🧪_Experiment_Configuration.py
│       └── 2_📊_Results_Dashboard.py
│
├── scripts/                        # Command-line scripts
│   ├── run_experiment.py           # Main experiment runner
│   └── run_pei_assessment.py       # PEI assessment script
│
├── tests/                          # Test suite
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_cycle_orchestrator.py
│   │   ├── test_ollama_interface.py
│   │   ├── test_tool_dispatcher.py
│   │   ├── test_memory_tools.py
│   │   └── test_similarity_monitor.py
│   ├── integration/
│   │   ├── test_full_cycle.py
│   │   └── test_experiment_flow.py
│   └── fixtures/
│       ├── sample_config.yaml
│       └── mock_responses.json
│
├── configs/                        # Experiment configurations (gitignored *.yaml)
│   ├── .gitkeep
│   └── sample-config.yaml          # Example configuration
│
├── data/                           # Persistent data (gitignored)
│   ├── .gitkeep
│   └── memory.db                   # Agent memory database
│
├── logs/                           # Experiment logs (gitignored *.jsonl)
│   └── .gitkeep
│
└── docs/                           # Documentation
    ├── architecture.md
    ├── prd.md
    ├── front-end-spec.md
    ├── brief.md
    └── SoftwareDesignSpecification.md
```

### Directory Purposes

**contreact_ollama/**: Main application package
- Organized by functional area (core, state, llm, tools, etc.)
- All production code lives here

**ui/**: Streamlit web interface
- Completely decoupled from backend
- Only interacts via file system

**scripts/**: Entry point scripts
- `run_experiment.py`: CLI for running experiments
- `run_pei_assessment.py`: CLI for PEI assessment

**tests/**: Comprehensive test suite
- `unit/`: Test individual components in isolation
- `integration/`: Test component interactions
- `fixtures/`: Test data and mocks

**configs/**: User-created experiment configurations
- `.gitkeep` to track directory
- `*.yaml` files gitignored
- `sample-config.yaml` committed as example

**data/**: Runtime data storage
- `memory.db`: Agent's persistent memory
- Gitignored to keep repository clean

**logs/**: Experiment output logs
- `*.jsonl` files gitignored
- `.gitkeep` to track directory

**docs/**: Project documentation
- Architecture and design documents
- All documentation committed to repository
