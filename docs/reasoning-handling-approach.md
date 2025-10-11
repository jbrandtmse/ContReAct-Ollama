# Reasoning Tag Handling in ContReAct-Ollama

## Overview

This document describes how `<thinking>` tags and other reasoning content are handled in the ContReAct-Ollama system, following best practices for autonomous agent design.

## The Hybrid Approach

We implement a **hybrid approach** that balances the need for comprehensive logging with efficient context window management:

### 1. Full Logging (Complete Reasoning Preserved)
**Location:** `LLM_INVOCATION` events in JSONL logs

All LLM responses, including full `<thinking>` tags, are logged in the `LLM_INVOCATION` event:

```json
{
  "event_type": "LLM_INVOCATION",
  "payload": {
    "response_message": {
      "role": "assistant",
      "content": "<thinking>My detailed reasoning here...</thinking>\n\n<list/>"
    }
  }
}
```

**Purpose:**
- Complete audit trail for debugging
- Analysis of agent reasoning patterns
- Research into decision-making processes
- Troubleshooting errors by tracing logic

### 2. Context Window Optimization (Reasoning Stripped)
**Location:** `reflection_history` passed to subsequent cycles

Thinking tags are stripped from reflections before adding them to the context:

```python
# Before (in reflection_history for next cycle):
"<list/>"

# Not:
"<thinking>My detailed reasoning here...</thinking>\n\n<list/>"
```

**Purpose:**
- Reduce token consumption by ~60-76% (based on research)
- Prevent context window overflow in long experiments
- Keep focus on actionable conclusions rather than intermediate steps
- Improve response consistency by reducing noise

## Implementation Details

### Response Parser (`response_parser.py`)

```python
def parse_ollama_response(response: Dict) -> Tuple[str, Any]:
    """
    Parse response and extract final reflection with thinking stripped.
    
    Note: Full content with thinking is already logged in LLM_INVOCATION event.
    """
    content = message.get("content", "")
    cleaned_content = strip_thinking_tags(content)  # Strip for context
    return ("FINAL_REFLECTION", cleaned_content)
```

### Cycle Orchestrator (`cycle_orchestrator.py`)

```python
# Log full response (with thinking)
self.logger.log_event(
    event_type=EventType.LLM_INVOCATION,
    payload={
        "response_message": serializable_message,  # Contains full content
        ...
    }
)

# Store stripped version in reflection history
response_type, data = self._parse_response(response)
if response_type == "FINAL_REFLECTION":
    agent_state.reflection_history.append(data)  # data has thinking stripped
```

## What Gets Logged Where

| Content Type | LLM_INVOCATION Log | CYCLE_END Log | Next Cycle Context |
|--------------|-------------------|---------------|-------------------|
| `<thinking>` tags | ✅ Full content | ✅ Full content | ❌ Stripped |
| Tool calls | ✅ Full content | N/A | ✅ Included |
| Final conclusions | ✅ Full content | ✅ Full content | ✅ Included |

## Rationale (Based on Research)

### Token Economics
- Chain-of-thought outputs generate lengthy responses (research shows 60-76% token overhead)
- For autonomous agents running hundreds of cycles, token costs compound quickly
- Stripping reasoning from context while preserving it in logs is optimal

### Context Window Management
- Models have finite context windows (e.g., 30K tokens in our experiments)
- Including full reasoning in every reflection quickly exhausts available context
- Stripped reflections allow for longer experiment runs

### Consistency and Quality
- Too much intermediate reasoning in context can confuse models
- Focusing on conclusions rather than steps improves coherence
- Full reasoning in logs enables debugging without context pollution

## Example: Cycle Flow

### Cycle 1
**LLM Response:**
```
<thinking>I need to explore my memory first to see what's stored</thinking>

<list/>
```

**Logged in LLM_INVOCATION:** Full content with thinking  
**Stored in reflection_history:** `<list/>`

### Cycle 2
**System Prompt Includes:**
```
## Your Previous Reflections

**Cycle 1**: <list/>
```

Note: Thinking is NOT in the system prompt, saving tokens.

**But in logs you can see:**
```json
{
  "cycle_number": 1,
  "event_type": "LLM_INVOCATION",
  "payload": {
    "response_message": {
      "content": "<thinking>I need to explore my memory first...</thinking>\n\n<list/>"
    }
  }
}
```

## Future Enhancements

Potential improvements to consider:

1. **Thinking Summaries:** Optionally create 1-sentence summaries of thinking to include in context
2. **Selective Retention:** Keep thinking for important decision points, strip for routine actions
3. **Retrieval System:** Store thinking separately and retrieve relevant reasoning when needed
4. **Structured Templates:** Use consistent formats for thinking to enable better compression

## References

- [Best Practices Research](perplexity-search-2025-10-11.md) - Detailed research on CoT handling
- Story 1.9: Final Reflection State Passing
- Response Parser Module Documentation
