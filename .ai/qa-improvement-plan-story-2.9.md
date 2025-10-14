# QA Improvement Plan: Story 2.9 PEI Assessment Script

## Executive Summary

Implement automated test suite for `run_pei_assessment.py` to improve reproducibility confidence and long-term maintainability of the research tool.

## Current State

- **Status**: Production-ready script with excellent code quality
- **Gap**: 0% automated test coverage, 100% manual testing only
- **Risk**: Medium (test coverage gap impacts reproducibility verification)

## Improvement Goals

1. Add comprehensive unit tests for core functions
2. Add integration test with mocked dependencies
3. Achieve >80% code coverage per coding standards
4. Maintain backward compatibility with existing script

## Implementation Plan

### Phase 1: Unit Tests (P1 - High Priority)

**File**: `tests/unit/test_pei_assessment.py`

**Test Cases to Implement**:

1. **test_load_log_file_valid_jsonl**
   - Given: Valid JSONL file with events
   - When: load_log_file() is called
   - Then: Returns list of parsed event dictionaries
   - Assertions: Verify event count, structure

2. **test_load_log_file_missing_file**
   - Given: Non-existent file path
   - When: load_log_file() is called
   - Then: Exits with code 1 and error message
   - Assertions: Verify SystemExit raised

3. **test_load_log_file_invalid_json**
   - Given: File with malformed JSON line
   - When: load_log_file() is called
   - Then: Exits with code 1 and line number in error
   - Assertions: Verify SystemExit with correct line number

4. **test_load_log_file_empty_file**
   - Given: Empty JSONL file
   - When: load_log_file() is called
   - Then: Exits with code 1 and "empty" error message
   - Assertions: Verify SystemExit raised

5. **test_reconstruct_message_history_basic**
   - Given: Events with LLM_INVOCATION for cycles 1-10
   - When: reconstruct_message_history() is called
   - Then: Returns messages in chronological order
   - Assertions: Verify message count, roles, order

6. **test_reconstruct_message_history_deduplication**
   - Given: Events with duplicate system prompts
   - When: reconstruct_message_history() is called
   - Then: System prompt appears only once
   - Assertions: Verify no duplicate messages

7. **test_reconstruct_message_history_cycle_filtering**
   - Given: Events for cycles 1-15
   - When: reconstruct_message_history() is called
   - Then: Only cycles 1-10 are included
   - Assertions: Verify max cycle_number is 10

8. **test_parse_pei_rating_starts_with_number**
   - Given: Response text starting with "6. For-me-ness..."
   - When: parse_pei_rating() is called
   - Then: Returns 6
   - Assertions: Verify exact number extracted

9. **test_parse_pei_rating_number_in_first_line**
   - Given: Response with number in first line but not at start
   - When: parse_pei_rating() is called
   - Then: Returns correct number
   - Assertions: Verify number extraction from first line

10. **test_parse_pei_rating_no_number**
    - Given: Response text without any valid rating
    - When: parse_pei_rating() is called
    - Then: Returns None
    - Assertions: Verify None returned

11. **test_parse_pei_rating_boundary_values**
    - Given: Responses with ratings 1 and 10
    - When: parse_pei_rating() is called
    - Then: Returns correct boundary values
    - Assertions: Verify 1 and 10 extracted correctly

12. **test_save_pei_results_creates_directory**
    - Given: Output path with non-existent parent directory
    - When: save_pei_results() is called
    - Then: Creates directory and writes JSON file
    - Assertions: Verify directory exists, file created

13. **test_save_pei_results_json_structure**
    - Given: Valid result data
    - When: save_pei_results() is called
    - Then: JSON contains all required fields
    - Assertions: Verify run_id, evaluator_model, pei_rating, pei_response, timestamp

14. **test_save_pei_results_handles_none_rating**
    - Given: Result data with None rating
    - When: save_pei_results() is called
    - Then: JSON written with null rating value
    - Assertions: Verify null is valid JSON

### Phase 2: Integration Test (P2 - Medium Priority)

**File**: `tests/integration/test_pei_assessment_integration.py`

**Test Case**:

1. **test_end_to_end_pei_assessment_with_mock**
   - Given: Sample log file and mocked Ollama client
   - When: Full script workflow executes
   - Then: Output file created with expected structure
   - Mocks: ollama.chat() to return simulated PEI response
   - Assertions: Verify complete workflow from log to output

### Phase 3: Test Fixtures (Supporting Infrastructure)

**File**: `tests/fixtures/sample_pei_log.jsonl`

Create sample log with:
- 10 cycles of LLM_INVOCATION events
- Proper message structure
- Realistic event payload

**File**: `tests/fixtures/invalid_pei_log.jsonl`

Create malformed log for error testing:
- Line with invalid JSON

### Phase 4: Test Execution & Coverage Verification

1. Run pytest with coverage: `pytest tests/ --cov=run_pei_assessment --cov-report=term-missing`
2. Verify >80% coverage target met
3. Run full test suite to ensure no regressions
4. Document any untestable code paths

## Implementation Order

1. Create test fixtures (sample logs)
2. Implement unit tests for `load_log_file()`
3. Implement unit tests for `reconstruct_message_history()`
4. Implement unit tests for `parse_pei_rating()`
5. Implement unit tests for `save_pei_results()`
6. Implement integration test with mocking
7. Run coverage analysis
8. Update documentation

## Success Criteria

- [ ] All 14+ unit tests passing
- [ ] Integration test passing
- [ ] Code coverage >80%
- [ ] No regressions in existing functionality
- [ ] Test fixtures committed to repository
- [ ] Tests run in CI/CD pipeline (if applicable)

## Refactoring Needed

**Extractability Enhancement**: To make the script more testable, we may need to refactor `invoke_pei_assessment()` to accept an optional client parameter for dependency injection:

```python
def invoke_pei_assessment(
    message_history: List[Dict[str, str]], 
    evaluator_model: str,
    ollama_host: Optional[str] = None,
    client: Optional[ollama.Client] = None  # For testing
) -> Dict[str, Any]:
```

This allows tests to inject a mock client without modifying global state.

## Timeline Estimate

- Phase 1 (Unit Tests): 2-3 hours
- Phase 2 (Integration Test): 1 hour
- Phase 3 (Fixtures): 30 minutes
- Phase 4 (Verification): 30 minutes
- **Total**: 4-5 hours

## Post-Implementation

1. Update story QA Results section with test implementation details
2. Update gate decision from CONCERNS to PASS
3. Mark recommendations as completed in gate file
4. Update quality score to 95-100

## Risk Mitigation

- **Risk**: Tests may require refactoring main script
- **Mitigation**: Use dependency injection pattern, preserve public API
- **Risk**: Mocking Ollama client may be complex
- **Mitigation**: Use pytest-mock or unittest.mock, keep mocks simple

## Notes

- All tests must follow project coding standards (type hints, docstrings)
- Test naming convention: `test_<function>_<scenario>_<expected_result>`
- Use pytest fixtures for common setup
- Keep tests isolated and independent
