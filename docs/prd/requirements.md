# Requirements

### Functional
1.  [cite_start]The system must parse a YAML configuration file to define experiment parameters like `run_id`, `model_name`, and `cycle_count`[cite: 501, 502, 625].
2.  [cite_start]The system must verify that the Ollama model specified in the configuration is available locally before an experiment begins[cite: 554, 633].
3.  [cite_start]The system must execute a user-defined number of operational cycles in a continuous loop[cite: 452, 453].
4.  [cite_start]The system must construct a complete prompt for the LLM at each step, including the system prompt, tool definitions, and the full message history[cite: 427, 428, 538].
5.  [cite_start]The system must provide a tool suite that includes persistent memory operations: `write`, `read`, `list`, `delete`, and `pattern_search`[cite: 72, 572].
6.  [cite_start]The system must provide a tool that allows the agent to send a synchronous message to a human operator via the console and wait for a text response[cite: 74, 581, 582].
7.  [cite_start]The system must log all significant events (e.g., `LLM_INVOCATION`, `TOOL_CALL`, `CYCLE_END`) to a `.jsonl` file, with each event formatted as a structured JSON object[cite: 393, 484, 615].
8.  [cite_start]The system must calculate the semantic similarity of an agent's reflections and provide advisory feedback if the cosine similarity exceeds 0.7 (moderate) or 0.8 (high)[cite: 78, 602, 603, 604].
9.  [cite_start]The system must provide a web UI that allows a user to create, view, and save experiment configuration files via a form[cite: 681, 682].
10. [cite_start]The system must provide a web UI that allows a user to select a completed `.jsonl` log file and view summary metrics and visualizations[cite: 688, 690, 691].
11. [cite_start]The system must include a standalone command-line script (`run_pei_assessment.py`) that performs the PEI assessment on a specified run log using a designated evaluator model[cite: 647, 648].

### Non-Functional
1.  [cite_start]The application must be developed in **Python, version 3.9 or higher**[cite: 407].
2.  [cite_start]The persistent memory store must be implemented using a lightweight, file-based database (TinyDB or SQLite) to ensure portability and simple setup[cite: 413, 414, 415].
3.  [cite_start]The core experimental logic must be fully decoupled from the web UI, with all communication handled via the file system (reading `.yaml` files and writing `.jsonl` files)[cite: 665, 705].
4.  [cite_start]The core ContReAct cycle must be implemented as a formal state machine to ensure a robust, modular, and debuggable architecture[cite: 418, 421].
5.  [cite_start]The exploration diversity module must use the `all-MiniLM-L6-v2` sentence transformer model by default for its balance of performance and resource efficiency on local machines[cite: 594, 8].
6.  [cite_start]The main experiment must be launchable from a command-line script that accepts a path to a configuration file as an argument[cite: 622, 623].
