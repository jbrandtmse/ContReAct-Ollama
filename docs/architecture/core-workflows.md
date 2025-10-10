# Core Workflows

### State Machine Workflow

The ContReAct cycle implemented as a formal state machine:

```mermaid
stateDiagram-v2
    [*] --> LOAD_STATE
    LOAD_STATE --> ASSEMBLE_PROMPT
    ASSEMBLE_PROMPT --> INVOKE_LLM
    INVOKE_LLM --> PARSE_RESPONSE
    PARSE_RESPONSE --> DISPATCH_TOOL: Tool Call Detected
    PARSE_RESPONSE --> FINALIZE_CYCLE: Final Reflection
    DISPATCH_TOOL --> ASSEMBLE_PROMPT: Tool Result Appended
    FINALIZE_CYCLE --> TERMINATE_OR_CONTINUE
    TERMINATE_OR_CONTINUE --> LOAD_STATE: More Cycles
    TERMINATE_OR_CONTINUE --> [*]: Complete
```

### ReAct Sub-Loop Sequence

Detailed sequence diagram for a single cycle's ReAct loop:

```mermaid
sequenceDiagram
    participant O as CycleOrchestrator
    participant P as PromptAssembler
    participant OI as OllamaInterface
    participant LLM as Ollama Server
    participant RP as ResponseParser
    participant TD as ToolDispatcher
    participant MT as MemoryTools
    
    O->>O: LOAD_STATE
    O->>P: build_prompt(agent_state)
    P-->>O: messages
    
    loop ReAct Loop (until final reflection)
        O->>OI: execute_chat_completion(messages)
        OI->>LLM: POST /api/chat
        LLM-->>OI: response
        OI-->>O: response
        
        O->>RP: parse_ollama_response(response)
        RP-->>O: (type, data)
        
        alt Tool Call
            O->>TD: dispatch(tool_name, args)
            TD->>MT: write/read/list/delete/pattern_search
            MT-->>TD: result
            TD-->>O: result
            O->>O: Append tool result to messages
        else Final Reflection
            O->>O: FINALIZE_CYCLE
        end
    end
```

### Complete Experiment Run Workflow

```mermaid
sequenceDiagram
    participant U as User
    participant CLI as run_experiment.py
    participant ER as ExperimentRunner
    participant CO as CycleOrchestrator
    participant L as JsonlLogger
    participant SM as SimilarityMonitor
    
    U->>CLI: python run_experiment.py --config config.yaml
    CLI->>ER: ExperimentRunner(config_path)
    ER->>ER: load_config()
    ER->>ER: initialize_services()
    ER->>CO: CycleOrchestrator(config, services...)
    
    loop For each cycle (1 to cycle_count)
        CO->>L: log_event(CYCLE_START)
        CO->>CO: execute_cycle()
        Note over CO: ReAct Loop (see above)
        CO->>SM: check_similarity(reflection_embedding)
        SM-->>CO: advisory_feedback or None
        CO->>L: log_event(CYCLE_END, metrics)
    end
    
    CO-->>ER: Experiment Complete
    ER-->>U: Success/Failure Message
```

### PEI Assessment Workflow

```mermaid
sequenceDiagram
    participant U as User
    participant S as run_pei_assessment.py
    participant OI as OllamaInterface
    participant LLM as Evaluator Model
    
    U->>S: python run_pei_assessment.py --run_log X.jsonl --evaluator model
    S->>S: Read and parse run log
    S->>S: Reconstruct message_history
    S->>S: Append PEI scale prompt
    S->>OI: execute_chat_completion(messages, temp=0.1)
    OI->>LLM: Invoke evaluator model
    LLM-->>OI: PEI rating response
    OI-->>S: PEI rating
    S->>S: Write to pei_results.jsonl
    S-->>U: Assessment complete
```
