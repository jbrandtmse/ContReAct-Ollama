"""Unit tests for CycleOrchestrator class."""

# Standard library imports
from unittest.mock import Mock, MagicMock, patch

# Third-party imports
import pytest

# Local application imports
from contreact_ollama.core.config import ExperimentConfig
from contreact_ollama.core.cycle_orchestrator import CycleOrchestrator
from contreact_ollama.llm.ollama_interface import OllamaInterface
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
        ollama_interface=mock_ollama_interface
    )
    
    # Assert config and ollama_interface stored correctly
    assert orchestrator.config == mock_config
    assert orchestrator.ollama_interface == mock_ollama_interface


def test_load_state_creates_agent_state_for_cycle(mock_config, mock_ollama_interface):
    """Test that _load_state creates AgentState with correct cycle number."""
    orchestrator = CycleOrchestrator(
        config=mock_config,
        ollama_interface=mock_ollama_interface
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
        ollama_interface=mock_ollama_interface
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
        ollama_interface=mock_ollama_interface
    )
    
    # Create AgentState
    agent_state = AgentState(
        run_id="test-run",
        cycle_number=1,
        model_name="llama3:latest"
    )
    
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
        ollama_interface=mock_ollama_interface
    )
    
    # Mock _execute_cycle to track calls
    orchestrator._execute_cycle = MagicMock(side_effect=lambda state: state)
    
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
        ollama_interface=mock_ollama_interface
    )
    
    # Track cycle numbers
    cycle_numbers = []
    
    # Mock _load_state to track cycle numbers
    original_load_state = orchestrator._load_state
    def track_load_state(cycle_number):
        cycle_numbers.append(cycle_number)
        return original_load_state(cycle_number)
    
    orchestrator._load_state = track_load_state
    
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
        ollama_interface=mock_ollama_interface
    )
    
    # Mock _execute_cycle
    orchestrator._execute_cycle = MagicMock(side_effect=lambda state: state)
    
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
        ollama_interface=mock_ollama_interface
    )
    
    # Mock _execute_cycle
    orchestrator._execute_cycle = MagicMock(side_effect=lambda state: state)
    
    # Run experiment
    orchestrator.run_experiment()
    
    # Verify _execute_cycle called exactly 10 times
    assert orchestrator._execute_cycle.call_count == 10


def test_run_experiment_console_output(mock_config, mock_ollama_interface, capsys):
    """Test that run_experiment prints correct console messages."""
    orchestrator = CycleOrchestrator(
        config=mock_config,
        ollama_interface=mock_ollama_interface
    )
    
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
