"""Unit tests for ToolDispatcher class."""

# Standard library imports
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

# Third-party imports
import pytest

# Local application imports
from contreact_ollama.tools.memory_tools import MemoryTools
from contreact_ollama.tools.tool_dispatcher import ToolDispatcher


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


@pytest.fixture
def tool_dispatcher(memory_tools):
    """Provide ToolDispatcher instance with real MemoryTools."""
    return ToolDispatcher(memory_tools=memory_tools)


def test_dispatch_calls_write_tool(tool_dispatcher):
    """Test that dispatch() correctly calls write tool."""
    result = tool_dispatcher.dispatch("write", {"key": "test", "value": "data"})
    
    # Assert write was successful
    assert "Wrote value to key 'test'" in result
    
    # Verify by reading back
    read_result = tool_dispatcher.dispatch("read", {"key": "test"})
    assert read_result == "data"


def test_dispatch_calls_read_tool(tool_dispatcher):
    """Test that dispatch() correctly calls read tool."""
    # Setup: write a value first
    tool_dispatcher.dispatch("write", {"key": "test_key", "value": "test_value"})
    
    # Test read
    result = tool_dispatcher.dispatch("read", {"key": "test_key"})
    
    # Assert correct value returned
    assert result == "test_value"


def test_dispatch_calls_list_tool(tool_dispatcher):
    """Test that dispatch() correctly calls list tool."""
    # Setup: write some values
    tool_dispatcher.dispatch("write", {"key": "key1", "value": "value1"})
    tool_dispatcher.dispatch("write", {"key": "key2", "value": "value2"})
    
    # Test list
    result = tool_dispatcher.dispatch("list", {})
    
    # Assert keys are listed
    assert "key1" in result
    assert "key2" in result


def test_dispatch_calls_delete_tool(tool_dispatcher):
    """Test that dispatch() correctly calls delete tool."""
    # Setup: write a value
    tool_dispatcher.dispatch("write", {"key": "test_key", "value": "test_value"})
    
    # Test delete
    result = tool_dispatcher.dispatch("delete", {"key": "test_key"})
    
    # Assert deletion confirmed
    assert "Deleted key 'test_key'" in result
    
    # Verify deletion
    read_result = tool_dispatcher.dispatch("read", {"key": "test_key"})
    assert "Error: Key 'test_key' not found" in read_result


def test_dispatch_calls_pattern_search_tool(tool_dispatcher):
    """Test that dispatch() correctly calls pattern_search tool."""
    # Setup: write some values
    tool_dispatcher.dispatch("write", {"key": "task_1", "value": "value1"})
    tool_dispatcher.dispatch("write", {"key": "task_2", "value": "value2"})
    tool_dispatcher.dispatch("write", {"key": "note_1", "value": "value3"})
    
    # Test pattern search
    result = tool_dispatcher.dispatch("pattern_search", {"pattern": "task"})
    
    # Assert matching keys found
    assert "task_1" in result
    assert "task_2" in result
    assert "note_1" not in result


def test_dispatch_invalid_tool_returns_error(tool_dispatcher):
    """Test that dispatch() returns error for invalid tool name."""
    result = tool_dispatcher.dispatch("invalid_tool", {})
    
    # Assert error message
    assert "Error: Tool 'invalid_tool' not found" in result


def test_dispatch_invalid_arguments_returns_error(tool_dispatcher):
    """Test that dispatch() returns error for invalid arguments."""
    # Missing required argument 'value'
    result = tool_dispatcher.dispatch("write", {"key": "test"})
    
    # Assert error message about invalid arguments
    assert "Error: Invalid arguments for tool 'write'" in result


def test_dispatch_wrong_argument_names_returns_error(tool_dispatcher):
    """Test that dispatch() returns error for wrong argument names."""
    # Wrong parameter name
    result = tool_dispatcher.dispatch("read", {"wrong_param": "value"})
    
    # Assert error message
    assert "Error: Invalid arguments for tool 'read'" in result


def test_get_tool_definitions_returns_all_tools(tool_dispatcher):
    """Test that get_tool_definitions() returns all 5 tools."""
    definitions = tool_dispatcher.get_tool_definitions()
    
    # Assert 5 tool definitions returned
    assert len(definitions) == 5
    
    # Extract tool names
    tool_names = [defn["function"]["name"] for defn in definitions]
    
    # Assert all expected tools present
    assert "write" in tool_names
    assert "read" in tool_names
    assert "list" in tool_names
    assert "delete" in tool_names
    assert "pattern_search" in tool_names


def test_get_tool_definitions_follows_ollama_format(tool_dispatcher):
    """Test that tool definitions follow Ollama JSON Schema format."""
    definitions = tool_dispatcher.get_tool_definitions()
    
    for defn in definitions:
        # Assert top-level structure
        assert "type" in defn
        assert defn["type"] == "function"
        assert "function" in defn
        
        # Assert function structure
        func = defn["function"]
        assert "name" in func
        assert "description" in func
        assert "parameters" in func
        
        # Assert parameters structure
        params = func["parameters"]
        assert "type" in params
        assert params["type"] == "object"
        assert "properties" in params
        assert "required" in params


def test_write_tool_definition_has_correct_schema(tool_dispatcher):
    """Test that write tool has correct parameter schema."""
    definitions = tool_dispatcher.get_tool_definitions()
    
    # Find write tool
    write_def = next(d for d in definitions if d["function"]["name"] == "write")
    
    # Assert parameters
    params = write_def["function"]["parameters"]
    assert "key" in params["properties"]
    assert "value" in params["properties"]
    assert params["required"] == ["key", "value"]


def test_read_tool_definition_has_correct_schema(tool_dispatcher):
    """Test that read tool has correct parameter schema."""
    definitions = tool_dispatcher.get_tool_definitions()
    
    # Find read tool
    read_def = next(d for d in definitions if d["function"]["name"] == "read")
    
    # Assert parameters
    params = read_def["function"]["parameters"]
    assert "key" in params["properties"]
    assert params["required"] == ["key"]


def test_list_tool_definition_has_no_parameters(tool_dispatcher):
    """Test that list tool has no required parameters."""
    definitions = tool_dispatcher.get_tool_definitions()
    
    # Find list tool
    list_def = next(d for d in definitions if d["function"]["name"] == "list")
    
    # Assert no required parameters
    params = list_def["function"]["parameters"]
    assert params["required"] == []
    assert params["properties"] == {}


def test_delete_tool_definition_has_correct_schema(tool_dispatcher):
    """Test that delete tool has correct parameter schema."""
    definitions = tool_dispatcher.get_tool_definitions()
    
    # Find delete tool
    delete_def = next(d for d in definitions if d["function"]["name"] == "delete")
    
    # Assert parameters
    params = delete_def["function"]["parameters"]
    assert "key" in params["properties"]
    assert params["required"] == ["key"]


def test_pattern_search_tool_definition_has_correct_schema(tool_dispatcher):
    """Test that pattern_search tool has correct parameter schema."""
    definitions = tool_dispatcher.get_tool_definitions()
    
    # Find pattern_search tool
    search_def = next(d for d in definitions if d["function"]["name"] == "pattern_search")
    
    # Assert parameters
    params = search_def["function"]["parameters"]
    assert "pattern" in params["properties"]
    assert params["required"] == ["pattern"]
