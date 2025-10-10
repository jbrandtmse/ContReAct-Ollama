"""Unit tests for MemoryTools class."""

# Standard library imports
import tempfile
from pathlib import Path

# Third-party imports
import pytest
from tinydb import TinyDB, Query

# Local application imports
from contreact_ollama.tools.memory_tools import MemoryTools


@pytest.fixture
def temp_db():
    """Provide temporary database path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_memory.db"
        yield str(db_path)


@pytest.fixture
def memory_tools(temp_db):
    """Provide MemoryTools instance with temp database."""
    memory = MemoryTools(db_path=temp_db, run_id="test-run")
    yield memory
    memory.close()


def test_init_creates_database_file(temp_db):
    """Test that initialization creates database file and directories."""
    # Create MemoryTools instance
    memory = MemoryTools(db_path=temp_db, run_id="test-run")
    
    # Assert database file created
    assert Path(temp_db).exists()
    
    # Assert parent directories created
    assert Path(temp_db).parent.exists()


def test_write_creates_new_entry(memory_tools):
    """Test that write() creates a new entry in the database."""
    result = memory_tools.write("test_key", "test_value")
    
    # Assert confirmation message returned
    assert "Wrote value to key 'test_key'" in result
    
    # Verify entry exists in database
    read_result = memory_tools.read("test_key")
    assert read_result == "test_value"


def test_write_updates_existing_entry(memory_tools):
    """Test that write() updates existing entry instead of creating duplicate."""
    # Write initial value
    memory_tools.write("test_key", "initial_value")
    
    # Write new value to same key
    result = memory_tools.write("test_key", "updated_value")
    
    # Assert update message returned
    assert "Updated key 'test_key' with new value" in result
    
    # Verify value is updated
    read_result = memory_tools.read("test_key")
    assert read_result == "updated_value"
    
    # Verify only one entry exists (not duplicate)
    Entry = Query()
    all_entries = memory_tools.db.search(
        (Entry.run_id == "test-run") & (Entry.key == "test_key")
    )
    assert len(all_entries) == 1


def test_read_returns_value(memory_tools):
    """Test that read() returns correct value for existing key."""
    # Write key-value pair
    memory_tools.write("test_key", "test_value")
    
    # Read value
    result = memory_tools.read("test_key")
    
    # Assert correct value returned
    assert result == "test_value"


def test_read_key_not_found_returns_error(memory_tools):
    """Test that read() returns error message for non-existent key."""
    # Read non-existent key
    result = memory_tools.read("nonexistent_key")
    
    # Assert error message returned
    assert "Error: Key 'nonexistent_key' not found" in result


def test_list_returns_all_keys(memory_tools):
    """Test that list() returns all keys in comma-separated format."""
    # Write multiple key-value pairs
    memory_tools.write("key1", "value1")
    memory_tools.write("key2", "value2")
    memory_tools.write("key3", "value3")
    
    # List all keys
    result = memory_tools.list()
    
    # Assert all keys in result
    assert "key1" in result
    assert "key2" in result
    assert "key3" in result
    
    # Verify comma-separated format
    keys = [k.strip() for k in result.split(",")]
    assert len(keys) == 3


def test_list_empty_returns_message(memory_tools):
    """Test that list() returns appropriate message for empty database."""
    # List keys with empty database
    result = memory_tools.list()
    
    # Assert "No keys stored" message
    assert "No keys stored" in result


def test_delete_removes_entry(memory_tools):
    """Test that delete() removes entry from database."""
    # Write key-value pair
    memory_tools.write("test_key", "test_value")
    
    # Delete key
    result = memory_tools.delete("test_key")
    
    # Assert confirmation message
    assert "Deleted key 'test_key'" in result
    
    # Verify entry removed from database
    read_result = memory_tools.read("test_key")
    assert "Error: Key 'test_key' not found" in read_result


def test_delete_key_not_found_returns_error(memory_tools):
    """Test that delete() returns error for non-existent key."""
    # Delete non-existent key
    result = memory_tools.delete("nonexistent_key")
    
    # Assert error message
    assert "Error: Key 'nonexistent_key' not found" in result


def test_pattern_search_finds_matching_keys(memory_tools):
    """Test that pattern_search() finds keys containing pattern."""
    # Write keys with different patterns
    memory_tools.write("task_1", "value1")
    memory_tools.write("task_2", "value2")
    memory_tools.write("note_1", "value3")
    
    # Search for "task" pattern
    result = memory_tools.pattern_search("task")
    
    # Assert matching keys returned
    assert "task_1" in result
    assert "task_2" in result
    assert "note_1" not in result


def test_pattern_search_no_matches_returns_message(memory_tools):
    """Test that pattern_search() returns message when no matches found."""
    # Write keys
    memory_tools.write("key1", "value1")
    
    # Search for non-matching pattern
    result = memory_tools.pattern_search("nonexistent")
    
    # Assert no matches message
    assert "No keys found matching pattern 'nonexistent'" in result


def test_run_id_isolation(temp_db):
    """Test that different run_ids are isolated from each other."""
    # Write data for run-1
    memory1 = MemoryTools(db_path=temp_db, run_id="run-1")
    memory1.write("shared_key", "value_from_run1")
    memory1.write("unique_key1", "value1")
    memory1.close()
    
    # Write data for run-2
    memory2 = MemoryTools(db_path=temp_db, run_id="run-2")
    memory2.write("shared_key", "value_from_run2")
    memory2.write("unique_key2", "value2")
    memory2.close()
    
    # Verify run-1 data isolation
    memory1 = MemoryTools(db_path=temp_db, run_id="run-1")
    try:
        assert memory1.read("shared_key") == "value_from_run1"
        assert memory1.read("unique_key1") == "value1"
        assert "Error: Key 'unique_key2' not found" in memory1.read("unique_key2")
        
        list1 = memory1.list()
        assert "shared_key" in list1
        assert "unique_key1" in list1
        assert "unique_key2" not in list1
    finally:
        memory1.close()
    
    # Verify run-2 data isolation
    memory2 = MemoryTools(db_path=temp_db, run_id="run-2")
    try:
        assert memory2.read("shared_key") == "value_from_run2"
        assert memory2.read("unique_key2") == "value2"
        assert "Error: Key 'unique_key1' not found" in memory2.read("unique_key1")
        
        list2 = memory2.list()
        assert "shared_key" in list2
        assert "unique_key2" in list2
        assert "unique_key1" not in list2
    finally:
        memory2.close()
