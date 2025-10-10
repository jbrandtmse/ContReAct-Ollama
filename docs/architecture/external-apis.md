# External APIs

### Ollama API Integration

**API Client**: ollama Python library (version 0.4.0+)

**Base URL**: Configurable via config.yaml, default: `http://localhost:11434`

**Authentication**: None (local server)

**Primary API Calls**:

#### 1. List Available Models

```python
client.list()
```

**Purpose**: Verify that required model is available locally before starting experiment

**Response**: List of model objects with names and metadata

**Error Handling**: Network errors should result in clear message instructing user to start Ollama server

#### 2. Chat Completion with Tools

```python
client.chat(
    model=model_name,
    messages=message_history,
    tools=tool_definitions,
    options=model_options
)
```

**Parameters**:
- `model` (str): Model tag (e.g., "llama3:latest")
- `messages` (List[Dict]): Message history in chat format
- `tools` (List[Dict]): Tool definitions in JSON schema format
- `options` (Dict): Generation parameters

**Response Structure**:
```python
{
    "message": {
        "role": "assistant",
        "content": str,  # May be empty if tool call present
        "tool_calls": [  # Present only if model wants to use tools
            {
                "function": {
                    "name": str,
                    "arguments": dict
                }
            }
        ]
    }
}
```

**Model Options Mapping** (from config.yaml to Ollama API):
- `seed`: Random seed for reproducibility
- `temperature`: Creativity control (0.0 = deterministic)
- `top_p`: Nucleus sampling threshold
- `num_predict`: Max tokens to generate
- `repeat_last_n`: Repetition prevention lookback
- `repeat_penalty`: Repetition penalty strength
- `num_ctx`: Context window size

**Error Handling**:
- `ollama.ResponseError`: Connection issues, invalid model
- Timeout errors: Long-running requests
- JSON parsing errors: Malformed tool calls
