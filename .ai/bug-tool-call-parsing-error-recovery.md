# Bug Report: Unhandled Tool Call Parsing Errors

**Bug ID**: TOOL-001  
**Date Reported**: 2025-10-16  
**Reported By**: Quinn (QA)  
**Severity**: HIGH - Production Blocker  
**Status**: ✅ RESOLVED  
**Resolution Date**: 2025-10-16

---

## Summary

Experiment crashes with status 500 when models produce malformed tool calls containing unicode escape sequences or mathematical notation. No graceful error recovery exists for server-side Ollama parsing failures.

---

## Reproduction Steps

1. Run experiment with model that imperfectly adheres to tool calling protocol (e.g., `gpt-oss:20b`)
2. Configure model to use `send_message_to_operator` tool
3. Provide operator responses that encourage detailed/technical output
4. Observe crash when model returns text with unicode (`\u03b6`) or complex number notation (`14.134725i`)

**Command:**
```bash
python scripts/run_experiment.py --config configs/gpt-oss-optimized-006.yaml
```

---

## Error Output

```
Error: Error during chat completion: error parsing tool call: raw='{"message":"Here is a brief overview of the Riemann Hypothesis:\n\n**Statement**: All non‑trivial zeros of the Riemann zeta function ζ(s) = ∑_{n=1}^{∞} n^{-s} (for Re(s) > 1, analytically continued to the complex plane) lie on the critical line Re(s) = 1/2.\n\n**Why it matters**: It is deeply connected to the distribution of prime numbers via the explicit formulas in analytic number theory. A proof would refine our understanding of primes and has implications for cryptography, random matrix theory, and quantum chaos.\n\n**Current status**: Despite extensive numerical verification (over 10^12 zeros have been checked) and many partial results (e.g., density theorems, zero‑free regions), a complete proof remains elusive. It is one of the seven Millennium Prize Problems, with a $1,000,000 reward for a correct solution.\n\n**Approaches**: Various strategies have been attempted:\n- **Explicit formulas** relating zeros to prime counting functions.\n- **Random matrix theory** analogies suggesting statistical properties of zeros.\n- **Algebraic geometry** via motives and L‑functions.\n- **Spectral theory** interpreting ζ(s) as a spectral determinant.\n\n**Interesting facts**:\n- The first few non‑trivial zeros are approximately 0.5 ± 14.134725i, 0.5 ± 21.022039i, etc.\n- The Riemann Hypothesis implies strong bounds on the error term in the prime number theorem.\n\nLet me know if you'd like more details, a different unsolved problem, or an interesting fact instead."}', err=invalid character 'i' in string escape code (status code: 500) (status code: -1)
```

---

## Root Cause

**Location**: Server-side Ollama JSON parser (before Python client receives response)

**Mechanism**:
1. Model violates tool calling protocol by returning structured content as raw text instead of proper tool call
2. Ollama server attempts to parse malformed structure as tool call
3. JSON parser encounters unicode escapes (`\u03b6`) and mathematical notation (`14.134725i`)
4. Parser fails with status 500, propagated as `ollama.ResponseError`
5. Current error handling in `ollama_interface.py` only catches errors AFTER successful response parsing

**Why Existing Error Handling Fails**:
- `ollama_interface.py` lines 84-117 handle malformed tool call **arguments**
- This error occurs during **initial response parsing** on server side
- Error is raised as `ollama.ResponseError` from `client.chat()` call, bypassing argument sanitization logic

---

## Impact Assessment

| Impact Category | Severity | Description |
|-----------------|----------|-------------|
| **Reliability** | HIGH | Experiments terminate unexpectedly, losing partial progress |
| **Data Collection** | HIGH | Unable to collect data from models with imperfect tool adherence |
| **User Experience** | MEDIUM | Confusing error messages, no actionable guidance |
| **Model Coverage** | HIGH | Limits testing to only models with perfect tool calling |

---

## Proposed Solution

### Implementation Plan

**Phase 1: Server-Side Error Recovery** (This Bug)
- Location: `contreact_ollama/llm/ollama_interface.py`
- Strategy: Wrap `client.chat()` call to catch tool parsing errors
- Graceful degradation: Convert malformed tool calls to text responses
- Log warnings for debugging and analysis

**Phase 2: Regression Testing** (This Bug)
- Location: `tests/unit/test_ollama_interface.py`
- Test case: Mock server-side parsing errors with unicode/mathematical notation
- Verify graceful degradation to text response

**Phase 3: NOT INCLUDED** ~~Prompt Engineering~~ (User Decision: Skip)
- ~~Add tool calling guidance to system prompts~~
- ~~Explicitly discourage special characters in tool arguments~~

---

## Test Cases

### Test 1: Unicode Escape Sequences
```python
# Mock response with unicode that breaks JSON parser
# Example: \u03b6 (Greek zeta)
# Expected: Graceful degradation to text response with warning
```

### Test 2: Mathematical Notation
```python
# Mock response with complex number notation
# Example: "14.134725i"
# Expected: Graceful degradation to text response with warning
```

### Test 3: Valid Tool Call (Regression)
```python
# Ensure valid tool calls still work correctly
# Expected: Normal tool call processing
```

---

## Acceptance Criteria

- [x] Experiments continue when models produce malformed tool calls
- [x] Malformed tool calls logged with clear warning messages
- [x] Malformed tool calls converted to text responses (FINAL_REFLECTION)
- [x] Regression tests pass for both malformed and valid tool calls (16/16 passing)
- [x] Documentation updated in bug report

---

## Related Files

- `contreact_ollama/llm/ollama_interface.py` (primary fix location)
- `tests/unit/test_ollama_interface.py` (test coverage)
- `contreact_ollama/llm/response_parser.py` (may need updates for consistency)

---

## Notes

- This affects primarily smaller or less-trained models
- Well-trained models (llama3.1, qwen2.5) rarely trigger this
- Graceful degradation is critical for research/experimentation use case
- Original error message should be preserved in logs for debugging

---

## Implementation Summary

**Changes Made:**

1. **Server-Side Error Recovery** (`contreact_ollama/llm/ollama_interface.py`)
   - Added `ollama.ResponseError` exception handler in `execute_chat_completion()`
   - Detects "error parsing tool call" messages from Ollama server
   - Extracts content from malformed tool calls using regex
   - Degrades gracefully to text response (FINAL_REFLECTION)
   - Logs detailed warnings for debugging

2. **Comprehensive Test Coverage** (`tests/unit/test_ollama_interface.py`)
   - Added 5 new test cases for malformed tool call scenarios
   - Test unicode escape sequences (Greek characters, mathematical notation)
   - Test complex number notation (`14.134725i`)
   - Test extraction failure fallback
   - Test non-tool-call errors are re-raised correctly
   - Regression test verifies valid tool calls still work
   - **Result: 16/16 tests passing**

**Verification:**
- All unit tests pass (16/16)
- Error handling verified for unicode and mathematical notation
- Graceful degradation confirmed
- Valid tool calls unaffected (regression protection)
