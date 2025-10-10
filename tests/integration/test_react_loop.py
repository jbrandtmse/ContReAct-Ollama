"""
Integration tests for full ReAct loop execution.
"""

# Standard library imports
from unittest.mock import Mock, MagicMock, patch

# Third-party imports
import pytest

# Local application imports
from contreact_ollama.core.config import ExperimentConfig
from contreact_ollama.core.cycle_orchestrator import CycleOrchestrator
from contreact_ollama.state.agent_state import AgentState


@pytest.fixture
def mock_config():
    """Provide mock ExperimentConfig for testing."""
    return ExperimentConfig(
        run_id="test-run",
        model_name="llama3:latest",
        cycle_count=1,
        ollama_client_config={"host": "http://localhost:11434"},
        model_options={"temperature": 0.7}
    )


@pytest.fixture
def mock_services():
    """Provide mocked services for testing."""
    services = {
        'ollama': Mock(),
        'logger': Mock(),
        'tool_dispatcher': Mock()
    }
    
    # Configure tool_dispatcher to return empty tool definitions
    services['tool_dispatcher'].get_tool_definitions.return_value = []
    
    return services


def test_full_react_loop_with_tool_call(mock_config, mock_services):
    """Test full ReAct loop with tool call followed by final reflection."""
    # Setup mocks
    # First call: tool call
    # Second call: final reflection
    mock_services['ollama'].execute_chat_completion.side_effect = [
        {
            "message": {
                "role": "assistant",
                "tool_calls": [
                    {
                        "function": {
                            "name": "write",
                            "arguments": {"key": "test", "value": "data"}
                        }
                    }
                ]
            }
        },
        {
            "message": {
                "role": "assistant",
                "content": "Task complete - data written"
            }
        }
    ]
    
    mock_services['tool_dispatcher'].dispatch.return_value = "Success: value written to key 'test'"
    
    # Create orchestrator
    orchestrator = CycleOrchestrator(
        config=mock_config,
        ollama_interface=mock_services['ollama'],
        tool_dispatcher=mock_services['tool_dispatcher'],
        logger=mock_services['logger']
    )
    
    # Run cycle
    agent_state = AgentState(
        run_id="test-run",
        cycle_number=1,
        model_name="llama3:latest"
    )
    
    result_state = orchestrator._execute_cycle(agent_state)
    
    # Assertions
    assert mock_services['ollama'].execute_chat_completion.call_count == 2
    assert mock_services['tool_dispatcher'].dispatch.called
    # Message history: assistant (with tool_calls), tool result, assistant (final reflection) = 3
    assert len(result_state.message_history) == 3
    assert "Task complete - data written" in result_state.reflection_history


def test_react_loop_logs_events(mock_config, mock_services):
    """Test that ReAct loop logs LLM_INVOCATION and TOOL_CALL events."""
    # Setup mocks
    mock_services['ollama'].execute_chat_completion.side_effect = [
        {
            "message": {
                "role": "assistant",
                "tool_calls": [
                    {
                        "function": {
                            "name": "read",
                            "arguments": {"key": "test"}
                        }
                    }
                ]
            }
        },
        {
            "message": {
                "role": "assistant",
                "content": "Read operation complete"
            }
        }
    ]
    
    mock_services['tool_dispatcher'].dispatch.return_value = "Value: test data"
    
    # Create orchestrator
    orchestrator = CycleOrchestrator(
        config=mock_config,
        ollama_interface=mock_services['ollama'],
        tool_dispatcher=mock_services['tool_dispatcher'],
        logger=mock_services['logger']
    )
    
    # Run cycle
    agent_state = AgentState(
        run_id="test-run",
        cycle_number=1,
        model_name="llama3:latest"
    )
    
    orchestrator._execute_cycle(agent_state)
    
    # Verify logging
    assert mock_services['logger'].log_event.call_count >= 3  # At least 2 LLM_INVOCATION + 1 TOOL_CALL


def test_react_loop_with_multiple_tool_calls(mock_config, mock_services):
    """Test ReAct loop with multiple tool calls in one response."""
    # Setup mocks
    mock_services['ollama'].execute_chat_completion.side_effect = [
        {
            "message": {
                "role": "assistant",
                "tool_calls": [
                    {
                        "function": {
                            "name": "write",
                            "arguments": {"key": "key1", "value": "value1"}
                        }
                    },
                    {
                        "function": {
                            "name": "write",
                            "arguments": {"key": "key2", "value": "value2"}
                        }
                    }
                ]
            }
        },
        {
            "message": {
                "role": "assistant",
                "content": "Both writes complete"
            }
        }
    ]
    
    mock_services['tool_dispatcher'].dispatch.return_value = "Success"
    
    # Create orchestrator
    orchestrator = CycleOrchestrator(
        config=mock_config,
        ollama_interface=mock_services['ollama'],
        tool_dispatcher=mock_services['tool_dispatcher'],
        logger=mock_services['logger']
    )
    
    # Run cycle
    agent_state = AgentState(
        run_id="test-run",
        cycle_number=1,
        model_name="llama3:latest"
    )
    
    result_state = orchestrator._execute_cycle(agent_state)
    
    # Assertions
    assert mock_services['tool_dispatcher'].dispatch.call_count == 2
    # Message history: assistant (with 2 tool calls), tool result 1, tool result 2, assistant (reflection)
    assert len(result_state.message_history) == 4


def test_react_loop_direct_reflection(mock_config, mock_services):
    """Test ReAct loop with immediate final reflection (no tools)."""
    # Setup mocks
    mock_services['ollama'].execute_chat_completion.return_value = {
        "message": {
            "role": "assistant",
            "content": "I'll explore this topic next cycle"
        }
    }
    
    # Create orchestrator
    orchestrator = CycleOrchestrator(
        config=mock_config,
        ollama_interface=mock_services['ollama'],
        tool_dispatcher=mock_services['tool_dispatcher'],
        logger=mock_services['logger']
    )
    
    # Run cycle
    agent_state = AgentState(
        run_id="test-run",
        cycle_number=1,
        model_name="llama3:latest"
    )
    
    result_state = orchestrator._execute_cycle(agent_state)
    
    # Assertions
    assert mock_services['ollama'].execute_chat_completion.call_count == 1
    assert mock_services['tool_dispatcher'].dispatch.call_count == 0
    assert "I'll explore this topic next cycle" in result_state.reflection_history


def test_react_loop_message_history_accumulation(mock_config, mock_services):
    """Test that message history accumulates correctly during ReAct loop."""
    # Setup mocks
    mock_services['ollama'].execute_chat_completion.side_effect = [
        {
            "message": {
                "role": "assistant",
                "tool_calls": [
                    {
                        "function": {
                            "name": "list_keys",
                            "arguments": {}
                        }
                    }
                ]
            }
        },
        {
            "message": {
                "role": "assistant",
                "content": "Found 5 keys"
            }
        }
    ]
    
    mock_services['tool_dispatcher'].dispatch.return_value = "Keys: key1, key2, key3, key4, key5"
    
    # Create orchestrator
    orchestrator = CycleOrchestrator(
        config=mock_config,
        ollama_interface=mock_services['ollama'],
        tool_dispatcher=mock_services['tool_dispatcher'],
        logger=mock_services['logger']
    )
    
    # Run cycle with existing message history
    agent_state = AgentState(
        run_id="test-run",
        cycle_number=1,
        model_name="llama3:latest",
        message_history=[
            {"role": "assistant", "content": "Previous cycle reflection"}
        ]
    )
    
    result_state = orchestrator._execute_cycle(agent_state)
    
    # Assertions
    # Initial: 1 (previous reflection)
    # Added: assistant (tool call), tool result, assistant (reflection) = 3
    # Total: 4
    assert len(result_state.message_history) == 4
    assert result_state.message_history[0]["content"] == "Previous cycle reflection"
    assert "role" in result_state.message_history[1]
    assert result_state.message_history[2]["role"] == "tool"


def test_react_loop_passes_correct_parameters_to_llm(mock_config, mock_services):
    """Test that ReAct loop passes correct parameters to LLM."""
    # Setup mocks
    mock_services['ollama'].execute_chat_completion.return_value = {
        "message": {
            "role": "assistant",
            "content": "Done"
        }
    }
    
    # Create orchestrator
    orchestrator = CycleOrchestrator(
        config=mock_config,
        ollama_interface=mock_services['ollama'],
        tool_dispatcher=mock_services['tool_dispatcher'],
        logger=mock_services['logger']
    )
    
    # Run cycle
    agent_state = AgentState(
        run_id="test-run",
        cycle_number=1,
        model_name="llama3:latest"
    )
    
    orchestrator._execute_cycle(agent_state)
    
    # Verify LLM was called with correct parameters
    call_args = mock_services['ollama'].execute_chat_completion.call_args
    assert call_args[1]['model_name'] == "llama3:latest"
    assert call_args[1]['options'] == {"temperature": 0.7}
    assert isinstance(call_args[1]['messages'], list)
    assert isinstance(call_args[1]['tools'], list)


def test_react_loop_includes_tool_call_id_in_results(mock_config, mock_services):
    """Test that tool result messages include tool_call_id field."""
    # Setup mocks with tool call containing id
    mock_services['ollama'].execute_chat_completion.side_effect = [
        {
            "message": {
                "role": "assistant",
                "tool_calls": [
                    {
                        "id": "call_abc123",
                        "function": {
                            "name": "write",
                            "arguments": {"key": "test", "value": "data"}
                        }
                    }
                ]
            }
        },
        {
            "message": {
                "role": "assistant",
                "content": "Complete"
            }
        }
    ]
    
    mock_services['tool_dispatcher'].dispatch.return_value = "Success"
    
    # Create orchestrator
    orchestrator = CycleOrchestrator(
        config=mock_config,
        ollama_interface=mock_services['ollama'],
        tool_dispatcher=mock_services['tool_dispatcher'],
        logger=mock_services['logger']
    )
    
    # Run cycle
    agent_state = AgentState(
        run_id="test-run",
        cycle_number=1,
        model_name="llama3:latest"
    )
    
    result_state = orchestrator._execute_cycle(agent_state)
    
    # Verify tool result message includes tool_call_id
    tool_result_msg = result_state.message_history[1]
    assert tool_result_msg["role"] == "tool"
    assert tool_result_msg["content"] == "Success"
    assert tool_result_msg["tool_call_id"] == "call_abc123"
