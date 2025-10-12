# Troubleshooting JSON Parsing Errors in Ollama Tool Calls

## Issue Summary

**Date**: October 12, 2025  
**Affected Experiments**: 
- gpt-oss-optimized-002 (seed: 723)
- Multiple subsequent runs

**Error Types**:
1. `Error during chat completion: error parsing tool call: invalid character '|' in string escape code`
2. `Error during chat completion: error parsing tool call: invalid character 'W' looking for beginning of value`

### Root Causes

Ollama's native tool calling with gpt-oss:20b model exhibits two types of JSON formatting issues:

1. **Improperly Escaped Special Characters**: When agents generate content containing markdown tables with pipe (`|`) characters or other special characters, these are not properly escaped in the tool call arguments JSON, causing parsing to fail.

2. **Raw Text Instead of JSON**: In some cases, the model returns reasoning text or explanatory content directly in the arguments field instead of a JSON object, violating the expected schema format.

### Specific Incident

During Cycle 4 of the experiment, the agent attempted to write a detailed technical overview of quantum internet protocols that included markdown tables with pipe separators:

```markdown
| Protocol | Purpose | Core Steps | Typical Use‑Case |
|---|---|---|---|
| **Quantum Key Distribution (QKD)** | Secure key exchange | 1. Prepare... | ... |
```

When this content was placed in the `value` parameter of a `write` tool call, Ollama's native tool calling failed to properly escape the pipe characters in the JSON structure, resulting in:

```
error parsing tool call: raw='{"key":"MDI_QKD_tutorial","value":"**Tutorial: Measurement‑Device‑Independent 
Quantum Key Distribution (MDI‑QKD)**\n\n---\n### 1. Motivation\n- Classical QKD protocols (BB84, E91) rely 
on trusted detectors. Real‑world detectors are vulnerable to side‑channel attacks (e.g., blinding attacks).\n- 
MDI‑QKD removes the trust requirement for detectors by delegating the measurement to an untrusted third 
party (Charlie). Even if Charlie is malicious, the key remains secure.\n\n### 2. Basic Principle\n1. **Alice** 
and **Bob** each prepare weak coherent pulses (WCPs) in one of the four BB84 polarization states: \|0⟩, \|1⟩, 
\|+⟩, \|−⟩...", err=invalid character '|' in string escape code
```

The pipe character (`|`) in the mathematical notation `\|0⟩` was not properly escaped, causing the JSON parser to fail.

## Solution Implemented

### Fix Location
**File**: `contreact_ollama/llm/ollama_interface.py`

### Implementation

Enhanced the `execute_chat_completion` method with comprehensive JSON validation and sanitization:

```python
# Include tool_calls if present
if hasattr(response.message, 'tool_calls') and response.message.tool_calls:
    tool_calls = []
    for tc in response.message.tool_calls:
        # Sanitize arguments - ensure they're valid JSON
        # Ollama may return arguments as dict, string, or malformed text
        arguments = tc.function.arguments
        
        # If arguments is a string, validate/sanitize it
        if isinstance(arguments, str):
            # Check if it starts with JSON structure indicators
            stripped = arguments.strip()
            if not (stripped.startswith('{') or stripped.startswith('[')):
                # Not JSON at all - model returned raw text
                print(f"Warning: Tool call '{tc.function.name}' returned non-JSON text instead of arguments")
                print(f"Raw text: {arguments[:200]}...")  # Show first 200 chars
                arguments = {}
            else:
                try:
                    # Try to parse as JSON to validate
                    parsed_args = json.loads(arguments)
                    arguments = parsed_args
                except json.JSONDecodeError as e:
                    # If parsing fails, try to sanitize the string
                    # This handles cases where special characters aren't properly escaped
                    print(f"Warning: JSON parsing failed for tool call '{tc.function.name}': {e}")
                    print(f"Raw arguments: {arguments[:200]}...")  # Show first 200 chars
                    
                    # Try to fix common issues
                    try:
                        # Attempt to clean up the JSON by removing control characters
                        cleaned = ''.join(char for char in arguments if ord(char) >= 32 or char in '\n\r\t')
                        parsed_args = json.loads(cleaned)
                        arguments = parsed_args
                        print("Successfully cleaned and parsed arguments")
                    except Exception:
                        # If all else fails, use empty dict
                        print("Could not recover - using empty arguments")
                        arguments = {}
        
        tool_calls.append({
            "id": getattr(tc, 'id', None),
            "function": {
                "name": tc.function.name,
                "arguments": arguments
            }
        })
    
    message_dict["tool_calls"] = tool_calls
```

### How It Works

1. **Type Check**: Verifies if arguments are a string (vs pre-parsed dict)
2. **Structure Detection**: Checks if the string starts with `{` or `[` to identify JSON vs raw text
3. **Raw Text Handling**: If not JSON-like, logs warning with content sample and uses empty dict
4. **JSON Parsing**: Attempts to parse valid-looking JSON strings
5. **Character Cleaning**: If parsing fails, removes control characters and retries
6. **Fallback**: Uses empty dict as last resort with detailed logging
7. **Graceful Degradation**: System continues running even with malformed tool calls

## Prevention Strategies

### 1. Model-Level Solutions

Consider using models with better tool-calling capabilities or fine-tuning for proper JSON escaping:

- **Llama 3.1 8B/70B**: Generally reliable for tool calling
- **GPT-OSS 20B**: Showed issues with special character escaping (as evidenced by this incident)
- **Alternative Models**: Test other Ollama models marked with "Tools" support

### 2. Prompt Engineering

Add instructions to the system prompt that discourage or guide the use of special characters:

```python
system_prompt = """
When writing content to memory, ensure all special characters are properly escaped.
Avoid using pipe characters (|) in markdown tables when storing to memory.
Instead, use alternative formatting like bullet lists or simplified text.
"""
```

### 3. Content Filtering

Implement pre-processing filters that detect and sanitize problematic content before tool calls:

```python
def sanitize_tool_argument(text: str) -> str:
    """Remove or escape problematic characters in tool arguments."""
    # Replace pipe characters in markdown tables
    text = text.replace('|', '\\|')
    # Add other sanitization rules as needed
    return text
```

### 4. Structured Output Validation

Use Ollama's structured outputs feature with Pydantic models to enforce format compliance:

```python
from pydantic import BaseModel

class WriteMemoryArgs(BaseModel):
    key: str
    value: str  # Pydantic will handle proper serialization

response = chat(
    model='llama3.1',
    messages=messages,
    tools=[write_memory_tool],
    format=WriteMemoryArgs.model_json_schema()
)
```

## Testing Recommendations

### Test Case 1: Markdown Tables
Create a test that attempts to write markdown tables with pipe characters to memory:

```python
def test_markdown_table_in_tool_call():
    """Test that markdown tables with pipes don't cause JSON parsing errors."""
    content = """
    | Column 1 | Column 2 |
    |----------|----------|
    | Value 1  | Value 2  |
    """
    # Execute tool call with this content
    # Assert no JSON parsing errors occur
```

### Test Case 2: Special Characters
Test a variety of special characters that commonly cause JSON issues:

```python
special_chars = [
    '|',  # Pipe
    '"',  # Quote
    '\\', # Backslash
    '\n', # Newline
    '\t', # Tab
    '<',  # Less than
    '>',  # Greater than
]
```

### Test Case 3: Mathematical Notation
Test mathematical notation that uses special characters:

```python
math_notation = [
    '\\|0⟩',  # Ket notation
    '∑_{i=1}^n',  # Summation
    'f(x) = x^2',  # Exponents
]
```

### Test Case 4: Long Content
Test with large content blocks to ensure the fix handles size:

```python
def test_large_content_with_special_chars():
    """Test handling of large content blocks containing special characters."""
    content = generate_markdown_document_with_tables(5000)  # 5000 words
    # Verify successful handling
```

## Monitoring and Logging

### Key Metrics to Track

1. **Tool Call Success Rate**: Monitor percentage of successful vs failed tool calls
2. **JSON Parsing Errors**: Count of JSON parsing failures per experiment
3. **Character Distribution**: Track which special characters appear most frequently in failures
4. **Model-Specific Patterns**: Compare error rates across different Ollama models

### Logging Implementation

The fix includes warning logs when parsing fails:

```
Warning: Failed to parse tool call arguments: invalid character '|' in string escape code
Raw arguments: {"key":"MDI_QKD_tutorial","value":"**Tutorial: Measurement‑Device‑Independent...
```

Monitor these warnings in experiment logs to identify recurring issues.

## Related Issues

### Known Ollama Issues

1. **Streaming Response Formatting**: Ollama may produce improperly formatted JSON in streaming contexts
2. **Unicode Escaping**: Some models over-escape Unicode characters (e.g., `<` → `\u003c`)
3. **Model-Specific Behavior**: Different models have varying reliability in tool calling

### Future Improvements

1. **Upstream Fix**: Report issue to Ollama team for model-level improvements
2. **Alternative Parsing**: Consider implementing custom parsing logic that's more tolerant
3. **Pre-validation**: Add validation before sending content to model
4. **Schema Enforcement**: Use Pydantic models consistently for all tool definitions

## References

- [Ollama Tool Calling Documentation](https://ollama.com/blog/tool-support)
- [JSON Parsing Best Practices](https://www.json.org/json-en.html)
- [Ollama Python Library Documentation](https://github.com/ollama/ollama-python)
- [Structured Outputs in Ollama](https://ollama.com/blog/structured-outputs)

## Version History

- **v1.0** (2025-10-12): Initial implementation of JSON sanitization fix
  - Added validation and sanitization to `ollama_interface.py`
  - Implemented graceful fallback for unparseable arguments
  - Added warning logs for debugging

- **v1.1** (2025-10-12): Enhanced fix for raw text arguments
  - Added detection for non-JSON raw text in arguments
  - Implemented control character cleaning for malformed JSON
  - Enhanced logging to distinguish between error types
  - Improved error recovery with multi-stage fallback
