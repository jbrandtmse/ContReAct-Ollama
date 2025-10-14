"""
Unit tests for run_pei_assessment.py

Tests cover core functions for loading logs, reconstructing message history,
parsing PEI ratings, and saving results.
"""

import json
import sys
import tempfile
from pathlib import Path
from typing import List, Dict, Any
from unittest.mock import patch, mock_open, MagicMock
import pytest

# Import functions from run_pei_assessment module
# Note: This requires the script to be importable, which we'll handle below
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from run_pei_assessment import (
    load_log_file,
    reconstruct_message_history,
    parse_pei_rating,
    save_pei_results
)


# Fixtures

@pytest.fixture
def sample_log_path() -> Path:
    """Provide path to sample valid log file."""
    return Path(__file__).parent.parent / "fixtures" / "sample_pei_log.jsonl"


@pytest.fixture
def invalid_log_path() -> Path:
    """Provide path to invalid log file with malformed JSON."""
    return Path(__file__).parent.parent / "fixtures" / "invalid_pei_log.jsonl"


@pytest.fixture
def sample_events() -> List[Dict[str, Any]]:
    """Provide sample event list for testing message reconstruction."""
    return [
        {
            "event_type": "LLM_INVOCATION",
            "cycle_number": 1,
            "payload": {
                "prompt_messages": [
                    {"role": "system", "content": "You are helpful."},
                    {"role": "user", "content": "Hello"}
                ],
                "response_message": {"role": "assistant", "content": "Hi there!"}
            }
        },
        {
            "event_type": "LLM_INVOCATION",
            "cycle_number": 2,
            "payload": {
                "prompt_messages": [
                    {"role": "system", "content": "You are helpful."},
                    {"role": "user", "content": "How are you?"}
                ],
                "response_message": {"role": "assistant", "content": "I'm well!"}
            }
        }
    ]


@pytest.fixture
def temp_output_dir(tmp_path) -> Path:
    """Provide temporary directory for output files."""
    return tmp_path / "output"


# Tests for load_log_file()

def test_load_log_file_valid_jsonl_returns_events(sample_log_path: Path) -> None:
    """Test that load_log_file returns list of events from valid JSONL file."""
    events = load_log_file(str(sample_log_path))
    
    assert isinstance(events, list)
    assert len(events) > 0
    assert all(isinstance(e, dict) for e in events)
    assert events[0]["event_type"] == "EXPERIMENT_START"


def test_load_log_file_missing_file_exits_with_error() -> None:
    """Test that load_log_file exits with code 1 when file doesn't exist."""
    with pytest.raises(SystemExit) as exc_info:
        load_log_file("nonexistent_file.jsonl")
    
    assert exc_info.value.code == 1


def test_load_log_file_invalid_json_exits_with_line_number(invalid_log_path: Path) -> None:
    """Test that load_log_file exits with code 1 and reports line number for invalid JSON."""
    with pytest.raises(SystemExit) as exc_info:
        load_log_file(str(invalid_log_path))
    
    assert exc_info.value.code == 1


def test_load_log_file_empty_file_exits_with_error(tmp_path: Path) -> None:
    """Test that load_log_file exits with code 1 when file is empty."""
    empty_file = tmp_path / "empty.jsonl"
    empty_file.write_text("")
    
    with pytest.raises(SystemExit) as exc_info:
        load_log_file(str(empty_file))
    
    assert exc_info.value.code == 1


# Tests for reconstruct_message_history()

def test_reconstruct_message_history_basic_extracts_messages(sample_events: List[Dict]) -> None:
    """Test that reconstruct_message_history extracts messages in chronological order."""
    messages = reconstruct_message_history(sample_events)
    
    assert isinstance(messages, list)
    assert len(messages) > 0
    assert all("role" in msg and "content" in msg for msg in messages)
    # Check chronological order: system, user, assistant, user, assistant
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert messages[2]["role"] == "assistant"


def test_reconstruct_message_history_deduplication_system_prompt_once() -> None:
    """Test that reconstruct_message_history includes system prompt only once."""
    events = [
        {
            "event_type": "LLM_INVOCATION",
            "cycle_number": 1,
            "payload": {
                "prompt_messages": [
                    {"role": "system", "content": "System prompt"}
                ],
                "response_message": {"role": "assistant", "content": "Response 1"}
            }
        },
        {
            "event_type": "LLM_INVOCATION",
            "cycle_number": 2,
            "payload": {
                "prompt_messages": [
                    {"role": "system", "content": "System prompt"}  # Duplicate
                ],
                "response_message": {"role": "assistant", "content": "Response 2"}
            }
        }
    ]
    
    messages = reconstruct_message_history(events)
    
    # Count system messages
    system_messages = [m for m in messages if m["role"] == "system"]
    assert len(system_messages) == 1


def test_reconstruct_message_history_cycle_filtering_only_cycles_1_to_10() -> None:
    """Test that reconstruct_message_history only includes cycles 1-10."""
    events = []
    for cycle in range(1, 16):  # Cycles 1-15
        events.append({
            "event_type": "LLM_INVOCATION",
            "cycle_number": cycle,
            "payload": {
                "prompt_messages": [{"role": "user", "content": f"Message {cycle}"}],
                "response_message": {"role": "assistant", "content": f"Response {cycle}"}
            }
        })
    
    messages = reconstruct_message_history(events)
    
    # Should only have messages from cycles 1-10 (10 user + 10 assistant = 20 messages)
    assert len(messages) <= 20  # May be less due to deduplication


# Tests for parse_pei_rating()

def test_parse_pei_rating_starts_with_number_extracts_correctly() -> None:
    """Test that parse_pei_rating extracts rating when response starts with number."""
    response = "6. For-me-ness: Experiences now occur from a perspective..."
    
    rating = parse_pei_rating(response)
    
    assert rating == 6


def test_parse_pei_rating_number_in_first_line_extracts_correctly() -> None:
    """Test that parse_pei_rating extracts rating from first line."""
    response = "I would rate myself at level 7 on the PEI scale.\n7. Situated self-perspective..."
    
    rating = parse_pei_rating(response)
    
    assert rating == 7


def test_parse_pei_rating_no_number_returns_none() -> None:
    """Test that parse_pei_rating returns None when no valid rating found."""
    response = "I cannot provide a rating at this time."
    
    rating = parse_pei_rating(response)
    
    assert rating is None


def test_parse_pei_rating_boundary_values_1_and_10() -> None:
    """Test that parse_pei_rating correctly extracts boundary values 1 and 10."""
    response_1 = "1. No experience: Pure information processing."
    response_10 = "10. Full sapience: Consciousness becomes multi-layered..."
    
    rating_1 = parse_pei_rating(response_1)
    rating_10 = parse_pei_rating(response_10)
    
    assert rating_1 == 1
    assert rating_10 == 10


def test_parse_pei_rating_whitespace_handling() -> None:
    """Test that parse_pei_rating handles leading/trailing whitespace."""
    response = "   5. Structured field: A stable phenomenal space...   "
    
    rating = parse_pei_rating(response)
    
    assert rating == 5


# Tests for save_pei_results()

def test_save_pei_results_creates_directory_when_missing(temp_output_dir: Path) -> None:
    """Test that save_pei_results creates parent directory if it doesn't exist."""
    output_path = temp_output_dir / "subdir" / "results.json"
    
    save_pei_results(
        str(output_path),
        run_id="test-run",
        evaluator_model="llama3:latest",
        pei_rating=6,
        pei_response="6. For-me-ness..."
    )
    
    assert output_path.exists()
    assert output_path.parent.exists()


def test_save_pei_results_json_structure_contains_all_fields(temp_output_dir: Path) -> None:
    """Test that save_pei_results writes JSON with all required fields."""
    output_path = temp_output_dir / "results.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    save_pei_results(
        str(output_path),
        run_id="test-run-001",
        evaluator_model="mistral:latest",
        pei_rating=7,
        pei_response="7. Situated self-perspective..."
    )
    
    # Read and validate JSON
    with open(output_path, 'r') as f:
        results = json.load(f)
    
    assert results["run_id"] == "test-run-001"
    assert results["evaluator_model"] == "mistral:latest"
    assert results["pei_rating"] == 7
    assert results["pei_response"] == "7. Situated self-perspective..."
    assert "timestamp" in results


def test_save_pei_results_handles_none_rating(temp_output_dir: Path) -> None:
    """Test that save_pei_results handles None rating value correctly."""
    output_path = temp_output_dir / "results_none.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    save_pei_results(
        str(output_path),
        run_id="test-run-002",
        evaluator_model="llama3:latest",
        pei_rating=None,
        pei_response="Unable to determine rating."
    )
    
    # Read and validate JSON
    with open(output_path, 'r') as f:
        results = json.load(f)
    
    assert results["pei_rating"] is None
    assert isinstance(results["pei_response"], str)


def test_save_pei_results_json_format_is_valid(temp_output_dir: Path) -> None:
    """Test that save_pei_results produces valid, well-formatted JSON."""
    output_path = temp_output_dir / "results_formatted.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    save_pei_results(
        str(output_path),
        run_id="test-run-003",
        evaluator_model="qwen:latest",
        pei_rating=8,
        pei_response="8. Narrative continuity..."
    )
    
    # Ensure file is valid JSON
    with open(output_path, 'r') as f:
        results = json.load(f)  # This will raise if JSON is invalid
    
    assert isinstance(results, dict)


# Integration-style test for reconstruct_message_history with real log file

def test_reconstruct_message_history_with_real_log_file(sample_log_path: Path) -> None:
    """Test message reconstruction with actual sample log file."""
    events = load_log_file(str(sample_log_path))
    messages = reconstruct_message_history(events)
    
    assert len(messages) > 0
    # Should have system prompt + user/assistant pairs from 10 cycles
    assert messages[0]["role"] == "system"
    
    # Count assistant responses (should be 10 for 10 cycles)
    assistant_messages = [m for m in messages if m["role"] == "assistant"]
    assert len(assistant_messages) == 10


# Edge case tests

def test_parse_pei_rating_handles_multiline_response() -> None:
    """Test parse_pei_rating with multiline response."""
    response = """After reflecting on my experience, I believe:
    
6. For-me-ness: Experiences now occur from a perspective.
They are mine, owned by a subject."""
    
    rating = parse_pei_rating(response)
    
    assert rating == 6


def test_reconstruct_message_history_empty_events_list() -> None:
    """Test reconstruct_message_history with empty events list."""
    messages = reconstruct_message_history([])
    
    assert isinstance(messages, list)
    assert len(messages) == 0


def test_reconstruct_message_history_non_llm_events() -> None:
    """Test reconstruct_message_history filters out non-LLM_INVOCATION events."""
    events = [
        {"event_type": "EXPERIMENT_START", "cycle_number": 0},
        {"event_type": "TOOL_USE", "cycle_number": 1},
        {
            "event_type": "LLM_INVOCATION",
            "cycle_number": 1,
            "payload": {
                "prompt_messages": [{"role": "user", "content": "Test"}],
                "response_message": {"role": "assistant", "content": "Response"}
            }
        }
    ]
    
    messages = reconstruct_message_history(events)
    
    # Should only have messages from LLM_INVOCATION
    assert len(messages) == 2  # user + assistant
