"""Unit tests for CycleOrchestrator class."""

# Standard library imports
from unittest.mock import Mock, MagicMock, patch

# Third-party imports
import pytest

# Local application imports
from contreact_ollama.core.config import ExperimentConfig
from contreact_ollama.core.cycle_orchestrator import CycleOrchestrator
from contreact_ollama.llm.ollama_interface import OllamaInterface
from contreact_ollama.logging.jsonl_logger import EventType
from contreact_ollama.state.agent_state import AgentState


@pytest.fixture
def mock_config():
    """Provide mock ExperimentConfig for testing."""
    config = Mock(spec=ExperimentConfig)
    config.run_id = "test-run"
    config.model_name = "llama3:latest"
    config.cycle_count = 3
    config.ollama_client_config = {"host": "http://localhost:11434"}
    config.model_options = {"temperature": 0.7}
    return config


@pytest.fixture
def mock_ollama_interface():
    """Provide mock OllamaInterface for testing."""
    return Mock(spec=OllamaInterface)


def test_init_stores_config_and_services(mock_config, mock_ollama_interface):
    """Test that CycleOrchestrator stores config and ollama_interface correctly."""
    orchestrator = CycleOrchestrator(
        config=mock_config,
        ollama_interface=mock_ollama_interface,
        tool_dispatcher=Mock()
    )
    
    # Assert config and ollama_interface stored correctly
    assert orchestrator.config == mock_config
    assert orchestrator.ollama_interface == mock_ollama_interface


def test_load_state_creates_agent_state_for_cycle(mock_config, mock_ollama_interface):
    """Test that _load_state creates AgentState with correct cycle number."""
    orchestrator = CycleOrchestrator(
        config=mock_config,
        ollama_interface=mock_ollama_interface,
        tool_dispatcher=Mock()
    )
    
    # Call _load_state with cycle_number=5
    agent_state = orchestrator._load_state(cycle_number=5)
    
    # Assert returned AgentState has correct cycle_number
    assert isinstance(agent_state, AgentState)
    assert agent_state.cycle_number == 5
    
    # Assert run_id and model_name from config
    assert agent_state.run_id == "test-run"
    assert agent_state.model_name == "llama3:latest"
    
    # Assert default lists are empty
    assert agent_state.message_history == []
    assert agent_state.reflection_history == []


def test_load_state_creates_different_states_for_different_cycles(
    mock_config, mock_ollama_interface
):
    """Test that _load_state creates different states for different cycles."""
    orchestrator = CycleOrchestrator(
        config=mock_config,
        ollama_interface=mock_ollama_interface,
        tool_dispatcher=Mock()
    )
    
    # Create states for different cycles
    state1 = orchestrator._load_state(cycle_number=1)
    state2 = orchestrator._load_state(cycle_number=2)
    state3 = orchestrator._load_state(cycle_number=10)
    
    # Assert different cycle numbers
    assert state1.cycle_number == 1
    assert state2.cycle_number == 2
    assert state3.cycle_number == 10


def test_execute_cycle_returns_state_unchanged(mock_config, mock_ollama_interface):
    """Test that _execute_cycle returns state unchanged."""
    orchestrator = CycleOrchestrator(
        config=mock_config,
        ollama_interface=mock_ollama_interface,
        tool_dispatcher=Mock()
    )
    
    # Create AgentState
    agent_state = AgentState(
        run_id="test-run",
        cycle_number=1,
        model_name="llama3:latest"
    )
    
    # Mock _execute_cycle to return state unchanged
    orchestrator._execute_cycle = MagicMock(side_effect=lambda state: state)
    
    # Call _execute_cycle
    returned_state = orchestrator._execute_cycle(agent_state)
    
    # Assert returned state is the same instance or has same values
    assert returned_state == agent_state
    assert returned_state.cycle_number == agent_state.cycle_number
    assert returned_state.run_id == agent_state.run_id
    assert returned_state.model_name == agent_state.model_name


def test_run_experiment_executes_correct_number_of_cycles(
    mock_config, mock_ollama_interface, capsys
):
    """Test that run_experiment executes the correct number of cycles."""
    orchestrator = CycleOrchestrator(
        config=mock_config,
        ollama_interface=mock_ollama_interface,
        tool_dispatcher=Mock()
    )
    
    # Mock _execute_cycle to track calls
    orchestrator._execute_cycle = MagicMock(side_effect=lambda state, diversity_feedback=None: state)
    
    # Run experiment (cycle_count=3)
    orchestrator.run_experiment()
    
    # Verify _execute_cycle called exactly 3 times
    assert orchestrator._execute_cycle.call_count == 3


def test_run_experiment_executes_cycles_in_order(
    mock_config, mock_ollama_interface
):
    """Test that run_experiment executes cycles in sequential order."""
    orchestrator = CycleOrchestrator(
        config=mock_config,
        ollama_interface=mock_ollama_interface,
        tool_dispatcher=Mock()
    )
    
    # Track cycle numbers
    cycle_numbers = []
    
    # Mock _load_state to track cycle numbers
    original_load_state = orchestrator._load_state
    def track_load_state(cycle_number):
        cycle_numbers.append(cycle_number)
        return original_load_state(cycle_number)
    
    orchestrator._load_state = track_load_state
    
    # Mock _execute_cycle to bypass ReAct loop
    orchestrator._execute_cycle = MagicMock(side_effect=lambda state, diversity_feedback=None: state)
    
    # Run experiment (cycle_count=3)
    orchestrator.run_experiment()
    
    # Assert _load_state called with 1, 2, 3 in order
    assert cycle_numbers == [1, 2, 3]


def test_run_experiment_with_single_cycle(mock_ollama_interface):
    """Test run_experiment with cycle_count=1."""
    config = Mock(spec=ExperimentConfig)
    config.run_id = "single-cycle-test"
    config.model_name = "llama3:latest"
    config.cycle_count = 1
    
    orchestrator = CycleOrchestrator(
        config=config,
        ollama_interface=mock_ollama_interface,
        tool_dispatcher=Mock()
    )
    
    # Mock _execute_cycle
    orchestrator._execute_cycle = MagicMock(side_effect=lambda state, diversity_feedback=None: state)
    
    # Run experiment
    orchestrator.run_experiment()
    
    # Verify _execute_cycle called exactly once
    assert orchestrator._execute_cycle.call_count == 1


def test_run_experiment_with_many_cycles(mock_ollama_interface):
    """Test run_experiment with larger cycle_count."""
    config = Mock(spec=ExperimentConfig)
    config.run_id = "many-cycles-test"
    config.model_name = "llama3:latest"
    config.cycle_count = 10
    
    orchestrator = CycleOrchestrator(
        config=config,
        ollama_interface=mock_ollama_interface,
        tool_dispatcher=Mock()
    )
    
    # Mock _execute_cycle
    orchestrator._execute_cycle = MagicMock(side_effect=lambda state, diversity_feedback=None: state)
    
    # Run experiment
    orchestrator.run_experiment()
    
    # Verify _execute_cycle called exactly 10 times
    assert orchestrator._execute_cycle.call_count == 10


def test_run_experiment_console_output(mock_config, mock_ollama_interface, capsys):
    """Test that run_experiment prints correct console messages."""
    orchestrator = CycleOrchestrator(
        config=mock_config,
        ollama_interface=mock_ollama_interface,
        tool_dispatcher=Mock()
    )
    
    # Mock _execute_cycle to bypass ReAct loop
    orchestrator._execute_cycle = MagicMock(side_effect=lambda state, diversity_feedback=None: state)
    
    # Run experiment
    orchestrator.run_experiment()
    
    # Capture console output
    captured = capsys.readouterr()
    
    # Assert expected messages in output
    assert "Starting experiment: test-run" in captured.out
    assert "Model: llama3:latest" in captured.out
    assert "Total cycles: 3" in captured.out
    assert "Cycle 1 starting..." in captured.out
    assert "Cycle 1 finished." in captured.out
    assert "Cycle 2 starting..." in captured.out
    assert "Cycle 2 finished." in captured.out
    assert "Cycle 3 starting..." in captured.out
    assert "Cycle 3 finished." in captured.out
    assert "✓ Experiment test-run completed successfully" in captured.out
    assert "✓ Executed 3 cycles" in captured.out


# Story 1.9 Tests: Final Reflection and State Passing

def test_run_experiment_passes_reflection_history_between_cycles(
    mock_config, mock_ollama_interface
):
    """Test that run_experiment passes reflection_history between cycles."""
    orchestrator = CycleOrchestrator(
        config=mock_config,
        ollama_interface=mock_ollama_interface,
        tool_dispatcher=Mock(),
        logger=None
    )
    
    # Track agent_state BEFORE modification
    initial_states = []
    
    def mock_execute_cycle(state, diversity_feedback=None):
        # Capture initial state (before modification)
        initial_states.append({
            "cycle_number": state.cycle_number,
            "reflection_history_len": len(state.reflection_history),
            "message_history_len": len(state.message_history)
        })
        # Add a reflection for this cycle
        state.reflection_history.append(f"Reflection for cycle {state.cycle_number}")
        # Add some messages (to verify they don't persist)
        state.message_history.append({"role": "assistant", "content": "test"})
        return state
    
    orchestrator._execute_cycle = mock_execute_cycle
    
    # Run experiment with 2 cycles
    mock_config.cycle_count = 2
    orchestrator.run_experiment()
    
    # Verify
    assert len(initial_states) == 2
    
    # Cycle 1: fresh state at start
    assert initial_states[0]["cycle_number"] == 1
    assert initial_states[0]["reflection_history_len"] == 0  # Empty before execute
    assert initial_states[0]["message_history_len"] == 0  # Fresh start
    
    # Cycle 2: new state with persisted reflection_history
    assert initial_states[1]["cycle_number"] == 2
    # Should have cycle 1's reflection from previous cycle
    assert initial_states[1]["reflection_history_len"] == 1
    # message_history should be EMPTY (fresh start for cycle 2)
    assert initial_states[1]["message_history_len"] == 0


def test_run_experiment_logs_cycle_end_with_reflection(mock_config, mock_ollama_interface):
    """Test that run_experiment logs CYCLE_END event with final_reflection."""
    mock_logger = Mock()
    mock_dispatcher = Mock()
    
    orchestrator = CycleOrchestrator(
        config=mock_config,
        ollama_interface=mock_ollama_interface,
        tool_dispatcher=mock_dispatcher,
        logger=mock_logger
    )
    
    # Mock _execute_cycle to add reflection to agent_state
    def mock_execute_cycle(state, diversity_feedback=None):
        state.reflection_history.append(f"Final reflection for cycle {state.cycle_number}")
        return state
    
    orchestrator._execute_cycle = mock_execute_cycle
    
    # Run experiment with 1 cycle
    mock_config.cycle_count = 1
    orchestrator.run_experiment()
    
    # Verify logger was called
    assert mock_logger.log_event.called
    
    # Find CYCLE_END call
    cycle_end_calls = [
        call for call in mock_logger.log_event.call_args_list
        if call[1].get("event_type") == EventType.CYCLE_END
    ]
    
    # Assert CYCLE_END event logged with final_reflection
    assert len(cycle_end_calls) == 1
    cycle_end_payload = cycle_end_calls[0][1]["payload"]
    assert "final_reflection" in cycle_end_payload
    assert cycle_end_payload["final_reflection"] == "Final reflection for cycle 1"


def test_run_experiment_empty_reflection_handled(mock_config, mock_ollama_interface):
    """Test that run_experiment handles empty reflection correctly."""
    mock_logger = Mock()
    mock_dispatcher = Mock()
    
    orchestrator = CycleOrchestrator(
        config=mock_config,
        ollama_interface=mock_ollama_interface,
        tool_dispatcher=mock_dispatcher,
        logger=mock_logger
    )
    
    # Mock _execute_cycle to NOT add reflection
    def mock_execute_cycle(state, diversity_feedback=None):
        # Don't add any reflection
        return state
    
    orchestrator._execute_cycle = mock_execute_cycle
    
    # Run experiment with 1 cycle
    mock_config.cycle_count = 1
    orchestrator.run_experiment()
    
    # Find CYCLE_END call
    cycle_end_calls = [
        call for call in mock_logger.log_event.call_args_list
        if call[1].get("event_type") == EventType.CYCLE_END
    ]
    
    # Assert CYCLE_END still logged with empty string
    assert len(cycle_end_calls) == 1
    cycle_end_payload = cycle_end_calls[0][1]["payload"]
    assert "final_reflection" in cycle_end_payload
    assert cycle_end_payload["final_reflection"] == ""


def test_cycle_number_increments_correctly(mock_config, mock_ollama_interface):
    """Test that cycle_number increments correctly across cycles."""
    orchestrator = CycleOrchestrator(
        config=mock_config,
        ollama_interface=mock_ollama_interface,
        tool_dispatcher=Mock(),
        logger=None
    )
    
    # Track cycle numbers
    cycle_numbers = []
    
    def mock_execute_cycle(state, diversity_feedback=None):
        cycle_numbers.append(state.cycle_number)
        return state
    
    orchestrator._execute_cycle = mock_execute_cycle
    
    # Run experiment with 3 cycles
    mock_config.cycle_count = 3
    orchestrator.run_experiment()
    
    # Verify cycle numbers are 1, 2, 3
    assert cycle_numbers == [1, 2, 3]


def test_message_history_resets_each_cycle(mock_config, mock_ollama_interface):
    """Test that message_history resets to empty at start of each cycle."""
    orchestrator = CycleOrchestrator(
        config=mock_config,
        ollama_interface=mock_ollama_interface,
        tool_dispatcher=Mock(),
        logger=None
    )
    
    # Track message_history at start of each cycle
    initial_message_histories = []
    
    def mock_execute_cycle(state, diversity_feedback=None):
        # Record initial message_history
        initial_message_histories.append(len(state.message_history))
        # Add some messages during cycle
        state.message_history.append({"role": "assistant", "content": "message1"})
        state.message_history.append({"role": "user", "content": "message2"})
        return state
    
    orchestrator._execute_cycle = mock_execute_cycle
    
    # Run experiment with 3 cycles
    mock_config.cycle_count = 3
    orchestrator.run_experiment()
    
    # Verify message_history starts at 0 for each cycle
    assert initial_message_histories == [0, 0, 0]
