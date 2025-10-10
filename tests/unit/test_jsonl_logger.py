"""Unit tests for JsonlLogger."""

# Standard library imports
import json
import tempfile
from pathlib import Path

# Third-party imports
import pytest

# Local application imports
from contreact_ollama.logging.jsonl_logger import JsonlLogger, EventType, LogRecord


@pytest.fixture
def temp_log_file():
    """Provide temporary log file path that gets cleaned up."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jsonl') as f:
        log_path = Path(f.name)
    yield log_path
    # Cleanup
    if log_path.exists():
        log_path.unlink()


def test_init_creates_log_file(temp_log_file):
    """Test that JsonlLogger creates log file on initialization."""
    logger = JsonlLogger(str(temp_log_file))
    assert temp_log_file.exists()
    logger.close()


def test_init_creates_parent_directories():
    """Test that JsonlLogger creates parent directories if needed."""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = Path(tmpdir) / "subdir" / "test.jsonl"
        logger = JsonlLogger(str(log_path))
        assert log_path.exists()
        assert log_path.parent.exists()
        logger.close()


def test_log_event_writes_valid_json_line(temp_log_file):
    """Test that log_event writes a valid JSON line."""
    logger = JsonlLogger(str(temp_log_file))
    
    logger.log_event(
        run_id="test-run",
        cycle_number=1,
        event_type=EventType.CYCLE_START,
        payload={"test": "data"}
    )
    
    logger.close()
    
    # Read and verify
    with open(temp_log_file, 'r') as f:
        line = f.readline()
        
    record = json.loads(line)  # Should not raise
    assert record['run_id'] == "test-run"
    assert record['cycle_number'] == 1
    assert record['event_type'] == "CYCLE_START"
    assert record['payload'] == {"test": "data"}
    assert 'timestamp' in record


def test_log_event_uses_iso8601_timestamp(temp_log_file):
    """Test that log_event uses ISO 8601 timestamp format."""
    logger = JsonlLogger(str(temp_log_file))
    
    logger.log_event(
        run_id="test-run",
        cycle_number=1,
        event_type=EventType.CYCLE_START,
        payload={}
    )
    
    logger.close()
    
    # Read logged record
    with open(temp_log_file, 'r') as f:
        line = f.readline()
    
    record = json.loads(line)
    timestamp = record['timestamp']
    
    # Verify ISO 8601 format (YYYY-MM-DDTHH:MM:SS.ffffffZ)
    assert timestamp.endswith('Z')
    assert 'T' in timestamp
    # Should be parseable as ISO format
    from datetime import datetime
    parsed = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    assert parsed is not None


def test_log_event_includes_all_fields(temp_log_file):
    """Test that log_event includes all required fields."""
    logger = JsonlLogger(str(temp_log_file))
    
    logger.log_event(
        run_id="test-run-123",
        cycle_number=42,
        event_type=EventType.CYCLE_END,
        payload={"key": "value", "number": 123}
    )
    
    logger.close()
    
    # Read logged record
    with open(temp_log_file, 'r') as f:
        line = f.readline()
    
    record = json.loads(line)
    
    # Assert all fields present
    assert 'timestamp' in record
    assert 'run_id' in record
    assert 'cycle_number' in record
    assert 'event_type' in record
    assert 'payload' in record
    
    # Verify values
    assert record['run_id'] == "test-run-123"
    assert record['cycle_number'] == 42
    assert record['event_type'] == "CYCLE_END"
    assert record['payload'] == {"key": "value", "number": 123}


def test_multiple_log_events_append(temp_log_file):
    """Test that multiple log_event calls append to the file."""
    logger = JsonlLogger(str(temp_log_file))
    
    # Log 3 events
    for i in range(1, 4):
        logger.log_event(
            run_id="test-run",
            cycle_number=i,
            event_type=EventType.CYCLE_START,
            payload={"cycle": i}
        )
    
    logger.close()
    
    # Read file
    with open(temp_log_file, 'r') as f:
        lines = f.readlines()
    
    # Assert 3 lines present
    assert len(lines) == 3
    
    # Assert each line is valid JSON
    for i, line in enumerate(lines, start=1):
        record = json.loads(line)
        assert record['cycle_number'] == i
        assert record['payload']['cycle'] == i


def test_logger_flush_ensures_immediate_write(temp_log_file):
    """Test that logger flushes data immediately (without closing)."""
    logger = JsonlLogger(str(temp_log_file))
    
    logger.log_event(
        run_id="test-run",
        cycle_number=1,
        event_type=EventType.CYCLE_START,
        payload={}
    )
    
    # Read file WITHOUT closing logger
    with open(temp_log_file, 'r') as f:
        content = f.read()
    
    # Event should be written due to flush
    assert len(content) > 0
    record = json.loads(content.strip())
    assert record['cycle_number'] == 1
    
    logger.close()


def test_context_manager_closes_file(temp_log_file):
    """Test that logger context manager properly closes file."""
    with JsonlLogger(str(temp_log_file)) as logger:
        logger.log_event(
            run_id="test-run",
            cycle_number=1,
            event_type=EventType.CYCLE_START,
            payload={}
        )
    
    # File should be closed now
    # We can verify by checking if file_handle is closed
    assert logger.file_handle.closed


def test_all_event_types_can_be_logged(temp_log_file):
    """Test that all EventType enum values can be logged."""
    logger = JsonlLogger(str(temp_log_file))
    
    event_types = [
        EventType.CYCLE_START,
        EventType.LLM_INVOCATION,
        EventType.TOOL_CALL,
        EventType.CYCLE_END
    ]
    
    for i, event_type in enumerate(event_types, start=1):
        logger.log_event(
            run_id="test-run",
            cycle_number=i,
            event_type=event_type,
            payload={}
        )
    
    logger.close()
    
    # Read and verify
    with open(temp_log_file, 'r') as f:
        lines = f.readlines()
    
    assert len(lines) == 4
    
    expected_types = ["CYCLE_START", "LLM_INVOCATION", "TOOL_CALL", "CYCLE_END"]
    for line, expected_type in zip(lines, expected_types):
        record = json.loads(line)
        assert record['event_type'] == expected_type


def test_empty_payload_is_valid(temp_log_file):
    """Test that empty payload is handled correctly."""
    logger = JsonlLogger(str(temp_log_file))
    
    logger.log_event(
        run_id="test-run",
        cycle_number=1,
        event_type=EventType.CYCLE_START,
        payload={}
    )
    
    logger.close()
    
    with open(temp_log_file, 'r') as f:
        line = f.readline()
    
    record = json.loads(line)
    assert record['payload'] == {}


def test_complex_payload_is_serialized(temp_log_file):
    """Test that complex nested payload is serialized correctly."""
    logger = JsonlLogger(str(temp_log_file))
    
    complex_payload = {
        "string": "value",
        "number": 123,
        "float": 45.67,
        "bool": True,
        "null": None,
        "list": [1, 2, 3],
        "nested": {
            "inner": "value"
        }
    }
    
    logger.log_event(
        run_id="test-run",
        cycle_number=1,
        event_type=EventType.TOOL_CALL,
        payload=complex_payload
    )
    
    logger.close()
    
    with open(temp_log_file, 'r') as f:
        line = f.readline()
    
    record = json.loads(line)
    assert record['payload'] == complex_payload
