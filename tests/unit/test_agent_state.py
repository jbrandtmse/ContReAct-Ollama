"""Unit tests for AgentState dataclass."""

# Standard library imports
from typing import List, Dict, Any

# Third-party imports
import pytest

# Local application imports
from contreact_ollama.state.agent_state import AgentState


def test_agent_state_initialization():
    """Test that AgentState can be initialized with required fields."""
    # Create AgentState with required fields
    state = AgentState(
        run_id="test-run-001",
        cycle_number=1,
        model_name="llama3:latest"
    )
    
    # Assert all fields set correctly
    assert state.run_id == "test-run-001"
    assert state.cycle_number == 1
    assert state.model_name == "llama3:latest"
    
    # Assert default lists are empty
    assert state.message_history == []
    assert state.reflection_history == []
    assert isinstance(state.message_history, list)
    assert isinstance(state.reflection_history, list)


def test_agent_state_with_message_history():
    """Test AgentState initialization with message history."""
    messages = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"}
    ]
    
    state = AgentState(
        run_id="test-run-002",
        cycle_number=2,
        model_name="llama3:latest",
        message_history=messages
    )
    
    assert len(state.message_history) == 3
    assert state.message_history[0]["role"] == "system"
    assert state.message_history[1]["content"] == "Hello"


def test_agent_state_with_reflection_history():
    """Test AgentState initialization with reflection history."""
    reflections = [
        "First reflection",
        "Second reflection",
        "Third reflection"
    ]
    
    state = AgentState(
        run_id="test-run-003",
        cycle_number=3,
        model_name="llama3:latest",
        reflection_history=reflections
    )
    
    assert len(state.reflection_history) == 3
    assert state.reflection_history[0] == "First reflection"
    assert state.reflection_history[2] == "Third reflection"


def test_agent_state_default_factory():
    """Test that default factory creates independent lists for each instance."""
    # Create two AgentState instances
    state1 = AgentState(
        run_id="test-run-004",
        cycle_number=1,
        model_name="llama3:latest"
    )
    
    state2 = AgentState(
        run_id="test-run-005",
        cycle_number=2,
        model_name="llama3:latest"
    )
    
    # Modify state1's message_history
    state1.message_history.append({"role": "user", "content": "Test"})
    
    # Assert message_history lists are independent (not shared)
    assert len(state1.message_history) == 1
    assert len(state2.message_history) == 0
    
    # Modify state1's reflection_history
    state1.reflection_history.append("Test reflection")
    
    # Assert reflection_history lists are independent
    assert len(state1.reflection_history) == 1
    assert len(state2.reflection_history) == 0


def test_agent_state_cycle_number_types():
    """Test that cycle_number accepts integer values."""
    state = AgentState(
        run_id="test-run-006",
        cycle_number=10,
        model_name="llama3:latest"
    )
    
    assert isinstance(state.cycle_number, int)
    assert state.cycle_number == 10


def test_agent_state_all_fields():
    """Test AgentState with all fields populated."""
    messages = [{"role": "user", "content": "Hello"}]
    reflections = ["Reflection 1"]
    
    state = AgentState(
        run_id="test-run-007",
        cycle_number=5,
        model_name="mistral:latest",
        message_history=messages,
        reflection_history=reflections
    )
    
    assert state.run_id == "test-run-007"
    assert state.cycle_number == 5
    assert state.model_name == "mistral:latest"
    assert len(state.message_history) == 1
    assert len(state.reflection_history) == 1
