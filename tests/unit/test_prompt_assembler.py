"""
Unit tests for PromptAssembler module.
"""

# Standard library imports
import pytest

# Local application imports
from contreact_ollama.llm.prompt_assembler import build_prompt
from contreact_ollama.state.agent_state import AgentState


def test_build_prompt_includes_system_message():
    """Test that build_prompt includes system message as first message."""
    # Setup
    agent_state = AgentState(
        run_id="test-run",
        cycle_number=1,
        model_name="llama3:latest",
        message_history=[],
        reflection_history=[]
    )
    system_prompt = "Test system prompt"
    tool_definitions = []
    
    # Execute
    messages = build_prompt(agent_state, system_prompt, tool_definitions)
    
    # Assert
    assert len(messages) == 1
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == system_prompt


def test_build_prompt_includes_message_history():
    """Test that build_prompt appends message history after system message."""
    # Setup
    agent_state = AgentState(
        run_id="test-run",
        cycle_number=1,
        model_name="llama3:latest",
        message_history=[
            {"role": "assistant", "content": "Hello"},
            {"role": "user", "content": "Hi there"}
        ],
        reflection_history=[]
    )
    system_prompt = "Test system prompt"
    tool_definitions = []
    
    # Execute
    messages = build_prompt(agent_state, system_prompt, tool_definitions)
    
    # Assert
    assert len(messages) == 3
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "assistant"
    assert messages[1]["content"] == "Hello"
    assert messages[2]["role"] == "user"
    assert messages[2]["content"] == "Hi there"


def test_build_prompt_appends_diversity_feedback():
    """Test that build_prompt appends diversity feedback to system prompt."""
    # Setup
    agent_state = AgentState(
        run_id="test-run",
        cycle_number=1,
        model_name="llama3:latest",
        message_history=[],
        reflection_history=[]
    )
    system_prompt = "Test system prompt"
    tool_definitions = []
    diversity_feedback = "Try exploring different topics"
    
    # Execute
    messages = build_prompt(agent_state, system_prompt, tool_definitions, diversity_feedback)
    
    # Assert
    assert len(messages) == 1
    assert messages[0]["role"] == "system"
    assert "Test system prompt" in messages[0]["content"]
    assert "Try exploring different topics" in messages[0]["content"]


def test_build_prompt_without_diversity_feedback():
    """Test that build_prompt works without diversity feedback."""
    # Setup
    agent_state = AgentState(
        run_id="test-run",
        cycle_number=1,
        model_name="llama3:latest",
        message_history=[],
        reflection_history=[]
    )
    system_prompt = "Test system prompt"
    tool_definitions = []
    
    # Execute
    messages = build_prompt(agent_state, system_prompt, tool_definitions)
    
    # Assert
    assert len(messages) == 1
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == system_prompt
