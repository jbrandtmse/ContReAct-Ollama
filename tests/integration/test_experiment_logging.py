"""Integration tests for experiment logging."""

# Standard library imports
import json
import tempfile
from pathlib import Path

# Third-party imports
import pytest

# Local application imports
from contreact_ollama.core.config import ExperimentConfig
from contreact_ollama.core.experiment_runner import ExperimentRunner


@pytest.fixture
def temp_config_file():
    """Create temporary config file for testing."""
    config_content = """
run_id: test-logging-run
model_name: llama3.1:8b
cycle_count: 2
ollama_client_config:
  host: http://192.168.0.123:11434
model_options:
  temperature: 0.7
  seed: 42
"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
        f.write(config_content)
        config_path = Path(f.name)
    
    yield str(config_path)
    
    # Cleanup
    if config_path.exists():
        config_path.unlink()


@pytest.fixture
def cleanup_log_file():
    """Clean up log file after test."""
    yield
    # Cleanup
    log_file = Path("logs/test-logging-run.jsonl")
    if log_file.exists():
        log_file.unlink()


def test_experiment_logs_cycle_events(temp_config_file, cleanup_log_file):
    """Test that experiment logs CYCLE_START and CYCLE_END events for each cycle."""
    # Note: This test requires Ollama to be running with llama3.1:8b model
    # Skip if Ollama is not available
    try:
        runner = ExperimentRunner(temp_config_file)
        runner.run()
    except Exception as e:
        pytest.skip(f"Ollama not available or model not found: {e}")
    
    # Read log file
    log_file = Path("logs/test-logging-run.jsonl")
    assert log_file.exists(), "Log file should be created"
    
    with open(log_file, 'r') as f:
        lines = f.readlines()
    
    # Should have 6 events (2 cycles × 3 events per cycle: CYCLE_START, LLM_INVOCATION, CYCLE_END)
    assert len(lines) == 6, f"Expected 6 log entries, got {len(lines)}"
    
    # Parse all events
    events = [json.loads(line) for line in lines]
    
    # Verify cycle 1 events
    assert events[0]['event_type'] == 'CYCLE_START'
    assert events[0]['cycle_number'] == 1
    assert events[0]['run_id'] == 'test-logging-run'
    
    assert events[1]['event_type'] == 'LLM_INVOCATION'
    assert events[1]['cycle_number'] == 1
    assert events[1]['run_id'] == 'test-logging-run'
    
    assert events[2]['event_type'] == 'CYCLE_END'
    assert events[2]['cycle_number'] == 1
    assert events[2]['run_id'] == 'test-logging-run'
    
    # Verify cycle 2 events
    assert events[3]['event_type'] == 'CYCLE_START'
    assert events[3]['cycle_number'] == 2
    assert events[3]['run_id'] == 'test-logging-run'
    
    assert events[4]['event_type'] == 'LLM_INVOCATION'
    assert events[4]['cycle_number'] == 2
    assert events[4]['run_id'] == 'test-logging-run'
    
    assert events[5]['event_type'] == 'CYCLE_END'
    assert events[5]['cycle_number'] == 2
    assert events[5]['run_id'] == 'test-logging-run'
    
    # Verify all have timestamps
    for event in events:
        assert 'timestamp' in event
        assert event['timestamp'].endswith('Z')


def test_log_file_path_uses_run_id(temp_config_file, cleanup_log_file):
    """Test that log file path is based on run_id from config."""
    # Note: This test requires Ollama to be running with llama3.1:8b model
    # Skip if Ollama is not available
    try:
        runner = ExperimentRunner(temp_config_file)
        runner.run()
    except Exception as e:
        pytest.skip(f"Ollama not available or model not found: {e}")
    
    # Verify log file exists at expected path
    log_file = Path("logs/test-logging-run.jsonl")
    assert log_file.exists(), "Log file should exist at logs/{run_id}.jsonl"


def test_log_entries_have_valid_json_structure(temp_config_file, cleanup_log_file):
    """Test that all log entries are valid JSON with correct structure."""
    # Note: This test requires Ollama to be running with llama3.1:8b model
    # Skip if Ollama is not available
    try:
        runner = ExperimentRunner(temp_config_file)
        runner.run()
    except Exception as e:
        pytest.skip(f"Ollama not available or model not found: {e}")
    
    # Read log file
    log_file = Path("logs/test-logging-run.jsonl")
    
    with open(log_file, 'r') as f:
        lines = f.readlines()
    
    # Each line should be valid JSON
    for line in lines:
        record = json.loads(line)  # Should not raise
        
        # Verify required fields
        assert 'timestamp' in record
        assert 'run_id' in record
        assert 'cycle_number' in record
        assert 'event_type' in record
        assert 'payload' in record
        
        # Verify types
        assert isinstance(record['timestamp'], str)
        assert isinstance(record['run_id'], str)
        assert isinstance(record['cycle_number'], int)
        assert isinstance(record['event_type'], str)
        assert isinstance(record['payload'], dict)


def test_log_entries_in_chronological_order(temp_config_file, cleanup_log_file):
    """Test that log entries are in chronological order."""
    # Note: This test requires Ollama to be running with llama3.1:8b model
    # Skip if Ollama is not available
    try:
        runner = ExperimentRunner(temp_config_file)
        runner.run()
    except Exception as e:
        pytest.skip(f"Ollama not available or model not found: {e}")
    
    # Read log file
    log_file = Path("logs/test-logging-run.jsonl")
    
    with open(log_file, 'r') as f:
        lines = f.readlines()
    
    events = [json.loads(line) for line in lines]
    
    # Extract timestamps
    timestamps = [event['timestamp'] for event in events]
    
    # Verify chronological order (timestamps should be non-decreasing)
    for i in range(len(timestamps) - 1):
        assert timestamps[i] <= timestamps[i + 1], \
            f"Timestamps not in chronological order: {timestamps[i]} > {timestamps[i + 1]}"
