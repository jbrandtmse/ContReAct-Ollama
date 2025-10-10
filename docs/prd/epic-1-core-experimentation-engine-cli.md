# Epic 1: Core Experimentation Engine & CLI

**Expanded Goal**: This epic will deliver the complete command-line version of the ContReAct-Ollama Experimental Platform. It focuses on establishing the project's foundation, implementing all core logic for running an experiment, and producing a valid, analyzable log file. By the end of this epic, a user will be able to faithfully replicate the paper's 10-cycle behavioral experiments.

---

### Story 1.1: Project Scaffolding and Environment Setup
**As a** Researcher, **I want** the complete project structure and development environment set up, **so that** I have a clean foundation to build the application.

**Acceptance Criteria**:
1. A Python virtual environment is created and activated
2. The complete project directory structure exists as defined in architecture.md (contreact_ollama/, ui/, scripts/, tests/, configs/, data/, logs/)
3. A `.gitignore` file is created with appropriate Python and project-specific exclusions
4. A `pyproject.toml` or `requirements.txt` file exists listing all required dependencies (streamlit, requests, tinydb, sentence-transformers, pyyaml, etc.)
5. All dependencies are successfully installed via `pip install`
6. A basic `README.md` exists with project title, description, and setup instructions
7. The git repository is initialized with an initial commit

**Dependencies**: None (first story)

---

### Story 1.2: Project Initialization and Configuration Loading
**As a** Researcher, **I want** a script that can initialize the project and load an experiment configuration from a YAML file, **so that** I can define and manage experiments reproducibly.

**Acceptance Criteria**:
1. [cite_start]A `run_experiment.py` script exists in the project's root directory[cite: 622].
2. [cite_start]The script can be executed with a `--config` argument pointing to a valid `.yaml` file[cite: 623, 625].
3. [cite_start]Upon execution, the script successfully parses the YAML file and prints its contents to the console[cite: 383, 626].
4. [cite_start]If the script is run with a path to a non-existent file, it exits gracefully with an informative error message[cite: 627].

**Dependencies**: Story 1.1

---

### Story 1.3: Ollama Connection and Model Verification
**As a** Researcher, **I want** the application to connect to my local Ollama server and verify the required model is available, **so that** I can ensure my experiment will run with the correct LLM.

**Acceptance Criteria**:
1. [cite_start]The script initializes an `OllamaInterface` that connects to the Ollama host specified in the config file[cite: 553].
2. [cite_start]The `OllamaInterface` successfully retrieves the list of locally available models from the Ollama server[cite: 554].
3. [cite_start]If the `model_name` from the config file is present in the list of available models, the script proceeds[cite: 554].
4. [cite_start]If the `model_name` is not found, the script terminates with a clear error message instructing the user to run `ollama pull <model_name>`[cite: 555].

**Dependencies**: Story 1.2

---

### Story 1.4: Basic Cycle Orchestration
**As a** Researcher, **I want** a basic `CycleOrchestrator` that can execute a defined number of empty cycles, **so that** the fundamental structure of the experiment loop is in place.

**Acceptance Criteria**:
1. [cite_start]The `CycleOrchestrator` runs for the exact number of cycles defined in the `cycle_count` parameter of the config file[cite: 452, 530].
2. A message indicating the start and end of each cycle (e.g., "Cycle 1 starting...", "Cycle 1 finished.") is printed to the console.
3. [cite_start]The script terminates successfully after the final cycle is completed[cite: 453].

**Dependencies**: Story 1.3

---

### Story 1.5: Implement Event Logging Service
**As a** Researcher, **I want** all major experimental events to be logged to a structured file, **so that** I have a complete, auditable record for post-hoc analysis.

**Acceptance Criteria**:
1. [cite_start]A `JsonlLogger` is implemented that writes to a file named `logs/<run_id>.jsonl`[cite: 613, 703].
2. [cite_start]The `CycleOrchestrator` uses the logger to record `CYCLE_START` and `CYCLE_END` events for each cycle[cite: 402].
3. [cite_start]Each line in the output `.jsonl` file is a valid JSON object conforming to the LogRecord schema[cite: 484, 616, 617].

**Dependencies**: Story 1.4

---

### Story 1.6: Implement Persistent Memory Tools
**As a** Researcher, **I want** the agent to have access to a persistent key-value memory store, **so that** it can retain information across multiple cycles.

**Acceptance Criteria**:
1. The TinyDB database is initialized in `data/memory.db` on first use if it doesn't exist
2. [cite_start]A `MemoryTools` class is implemented with `write`, `read`, `list`, `delete`, and `pattern_search` methods[cite: 569, 572].
3. [cite_start]These methods correctly interact with a file-based database (TinyDB or SQLite)[cite: 475, 476, 570].
4. [cite_start]A `ToolDispatcher` is implemented that can receive a tool name and arguments and invoke the corresponding method in the `MemoryTools` class[cite: 391, 392, 443].

**Dependencies**: Story 1.5

---

### Story 1.7: Implement Operator Communication Tool
**As a** Researcher, **I want** the agent to be able to send me synchronous messages and wait for my response, **so that** I can interact with it during an experiment as the operator.

**Acceptance Criteria**:
1. [cite_start]A `send_message_to_operator` function is implemented[cite: 581].
2. [cite_start]When invoked by the `ToolDispatcher`, the function prints the agent's message to the console[cite: 583].
3. [cite_start]The script then blocks and waits for the operator to type a response and press Enter[cite: 584, 585].
4. [cite_start]The text entered by the operator is returned as the output of the tool call[cite: 586].

**Dependencies**: Story 1.6

---

### Story 1.8: Full ReAct Loop with Tool Usage
**As a** Researcher, **I want** the orchestrator to execute a full ReAct (Reason-Act) loop within a single cycle, **so that** the agent can use tools to achieve its goals.

**Acceptance Criteria**:
1. [cite_start]The `CycleOrchestrator` assembles a prompt and calls the LLM via the `OllamaInterface`[cite: 397, 532].
2. [cite_start]The orchestrator correctly parses a response containing a tool call from the LLM[cite: 439, 545].
3. [cite_start]The `ToolDispatcher` executes the requested tool (e.g., a memory operation) and gets a result[cite: 399].
4. [cite_start]`LLM_INVOCATION` and `TOOL_CALL` events are correctly logged[cite: 402, 497, 498].
5. [cite_start]The orchestrator calls the LLM again with the tool's result appended to the message history, continuing the loop[cite: 400, 445].

**Dependencies**: Story 1.7

---

### Story 1.9: Implement Final Reflection and State Passing
**As a** Researcher, **I want** the agent's final thought in a cycle to be recognized as its reflection and for its state to persist to the next cycle, **so that** the experiment is continuous.

**Acceptance Criteria**:
1. [cite_start]When an LLM response does not contain a tool call, the orchestrator identifies it as the "final reflection" for the cycle[cite: 447, 448].
2. [cite_start]The `CYCLE_END` log event payload includes the text of the final reflection[cite: 499].
3. [cite_start]The complete message history, including the final reflection, is correctly passed as the starting state for the next cycle[cite: 403, 423].

**Dependencies**: Story 1.8

---

### Story 1.10: Implement Exploration Diversity Module
**As a** Researcher, **I want** the system to monitor for repetitive agent reflections and provide feedback, **so that** I can study how the agent responds to guidance on exploration diversity.

**Acceptance Criteria**:
1. [cite_start]A `SimilarityMonitor` is implemented that uses the `all-MiniLM-L6-v2` model to generate embeddings for final reflections[cite: 597, 593].
2. [cite_start]At the end of a cycle, the monitor calculates the cosine similarity between the new reflection and all previous ones[cite: 602].
3. [cite_start]If similarity exceeds the defined thresholds (0.7 or 0.8), the corresponding advisory feedback message is added to the system prompt for the *next* LLM invocation[cite: 78, 432, 603, 604].
4. [cite_start]If no threshold is met, no feedback is provided[cite: 605].

**Dependencies**: Story 1.9
