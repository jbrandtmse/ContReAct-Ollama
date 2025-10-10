# Source Tree

This document describes the directory structure and organization of the ContReAct-Ollama project.

## Directory Structure

```
ContReAct-Ollama/
├── contreact_ollama/          # Main application package
│   ├── __init__.py
│   ├── constants.py           # Project-wide constants
│   ├── core/                  # Core experiment execution
│   │   ├── __init__.py
│   │   ├── config.py          # Configuration data models
│   │   ├── cycle_orchestrator.py  # Cycle execution orchestrator
│   │   └── experiment_runner.py   # Main experiment runner
│   ├── state/                 # State management
│   │   ├── __init__.py
│   │   └── agent_state.py     # Agent state data models
│   ├── llm/                   # LLM interface layer
│   │   ├── __init__.py
│   │   └── ollama_interface.py    # Ollama API client wrapper
│   ├── tools/                 # Agent tool implementations
│   │   └── __init__.py
│   ├── diversity/             # Exploration diversity monitoring
│   │   └── __init__.py
│   └── logging/               # Event logging
│       ├── __init__.py
│       └── jsonl_logger.py    # JSONL event logger
├── ui/                        # Streamlit web interface
│   ├── dashboard.py           # Main dashboard entry point
│   └── pages/                 # Dashboard page modules
├── scripts/                   # Command-line utilities
│   └── run_experiment.py      # CLI experiment runner
├── tests/                     # Test suite
│   ├── __init__.py
│   ├── fixtures/              # Test fixtures and sample data
│   │   └── sample_config.yaml
│   ├── unit/                  # Unit tests
│   │   ├── test_agent_state.py
│   │   ├── test_cycle_orchestrator.py
│   │   ├── test_experiment_runner.py
│   │   ├── test_jsonl_logger.py
│   │   └── test_ollama_interface.py
│   └── integration/           # Integration tests
│       ├── test_cli.py
│       ├── test_experiment_flow.py
│       └── test_experiment_logging.py
├── configs/                   # Experiment configuration files
│   ├── .gitkeep
│   └── sample-config.yaml     # Sample experiment configuration
├── data/                      # Persistent agent memory storage
│   └── .gitkeep
├── logs/                      # Experiment output logs
│   └── .gitkeep
├── docs/                      # Project documentation
│   ├── brief.md               # Project overview
│   ├── prd.md                 # Product requirements (legacy)
│   ├── architecture.md        # Technical architecture (legacy)
│   ├── SoftwareDesignSpecification.md
│   ├── front-end-spec.md
│   ├── po-validation-report.md
│   ├── WhatDoLLMAgentsDoWhenLeftAlone.md
│   ├── prd/                   # Sharded PRD documents
│   │   ├── index.md
│   │   ├── goals-and-background-context.md
│   │   ├── requirements.md
│   │   ├── epic-list.md
│   │   ├── epic-1-core-experimentation-engine-cli.md
│   │   ├── epic-2-web-interface-analysis-tools.md
│   │   ├── technical-assumptions.md
│   │   ├── user-interface-design-goals.md
│   │   ├── appendix.md
│   │   ├── next-steps.md
│   │   └── checklist-results-report.md
│   ├── architecture/          # Sharded architecture documents
│   │   ├── index.md
│   │   ├── introduction.md
│   │   ├── high-level-architecture.md
│   │   ├── components.md
│   │   ├── core-workflows.md
│   │   ├── data-models.md
│   │   ├── tech-stack.md
│   │   ├── coding-standards.md
│   │   ├── api-specification.md
│   │   ├── backend-architecture.md
│   │   ├── frontend-architecture.md
│   │   ├── database-schema.md
│   │   ├── external-apis.md
│   │   ├── security-and-performance.md
│   │   ├── error-handling-strategy.md
│   │   ├── testing-strategy.md
│   │   ├── deployment-architecture.md
│   │   ├── monitoring-and-observability.md
│   │   ├── development-workflow.md
│   │   ├── unified-project-structure.md
│   │   └── checklist-results-report.md
│   ├── qa/                    # Quality assurance
│   │   └── gates/             # QA gate definitions
│   │       ├── 1.1-project-scaffolding.yml
│   │       ├── 1.2-project-initialization.yml
│   │       ├── 1.3-ollama-connection.yml
│   │       ├── 1.4-basic-cycle-orchestration.yml
│   │       └── 1.5-event-logging-service.yml
│   └── stories/               # User stories and development tasks
│       ├── 1.1.project-scaffolding.md
│       ├── 1.2.project-initialization.md
│       ├── 1.3.ollama-connection.md
│       ├── 1.4.basic-cycle-orchestration.md
│       ├── 1.5.event-logging-service.md
│       ├── 1.6.persistent-memory-tools.md
│       ├── 1.7.operator-communication.md
│       ├── 1.8.full-react-loop.md
│       ├── 1.9.final-reflection-state-passing.md
│       ├── 1.10.exploration-diversity-module.md
│       ├── 2.1.basic-streamlit-app.md
│       ├── 2.2.experiment-configuration-form.md
│       ├── 2.3.configuration-file-saving.md
│       ├── 2.4.configuration-file-loading.md
│       ├── 2.5.results-dashboard-run-selector.md
│       ├── 2.6.display-summary-metrics.md
│       ├── 2.7.display-conversation-log.md
│       ├── 2.8.interactive-charts.md
│       └── 2.9.pei-assessment-script.md
├── .gitignore                 # Git ignore rules
├── LICENSE                    # MIT License
├── README.md                  # Project readme
├── CONTRIBUTING.md            # Contribution guidelines
├── pyproject.toml             # Python project configuration
├── review_checklist.md        # Code review checklist
├── review_summary.md          # Review summary document
├── gap_analysis.md            # Gap analysis document
└── ContReAct-Ollama.code-workspace  # VS Code workspace config
```

## Module Organization

### contreact_ollama/
The main application package follows a layered architecture:

- **core/** - Top-level experiment orchestration and configuration
- **state/** - State management and data models
- **llm/** - LLM provider interface abstraction
- **tools/** - Agent tool implementations (memory, communication, etc.)
- **diversity/** - Exploration diversity monitoring
- **logging/** - Structured event logging

### ui/
Streamlit-based web interface for experiment management and analysis:

- **dashboard.py** - Main entry point
- **pages/** - Individual dashboard pages

### tests/
Comprehensive test suite following the source code structure:

- **unit/** - Unit tests for individual components
- **integration/** - Integration tests for complete workflows
- **fixtures/** - Shared test data and configurations

### docs/
Project documentation with sharded architecture:

- **prd/** - Product requirements organized by section
- **architecture/** - Technical architecture by topic
- **qa/gates/** - Quality assurance gate definitions
- **stories/** - User stories and implementation tasks

## Key Files

- **pyproject.toml** - Python project metadata and dependencies
- **configs/sample-config.yaml** - Template experiment configuration
- **scripts/run_experiment.py** - CLI tool for running experiments
- **README.md** - Project overview and getting started guide

## Naming Conventions

- **Directories**: lowercase with underscores (snake_case)
- **Python files**: lowercase with underscores (snake_case)
- **Test files**: prefixed with `test_` matching the module under test
- **Documentation**: kebab-case for multi-word files
- **Configuration**: kebab-case or snake_case depending on context

## Data Directories

- **data/** - TinyDB files for persistent agent memory (generated at runtime)
- **logs/** - JSONL experiment logs (generated at runtime)
- **configs/** - User-created experiment configurations

These directories use `.gitkeep` files to ensure they exist in version control while ignoring runtime-generated content.
