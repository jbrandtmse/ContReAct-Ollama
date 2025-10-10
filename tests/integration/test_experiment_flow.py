"""Integration tests for full experiment flow."""

# Standard library imports
import os
import tempfile
from pathlib import Path

# Third-party imports
import pytest
import yaml

# Local application imports
from contreact_ollama.core.experiment_runner import ExperimentRunner
from contreact_ollama.core.cycle_orchestrator import CycleOrchestrator


@pytest.fixture
def temp_config_file():
    """Create a temporary config file for testing."""
    config_data = {
        'run_id': 'integration-test-001',
        'model_name': 'llama3:latest',
        'cycle_count': 2,
        'ollama_client_config': {
            'host': 'http://localhost:11434'
        },
        'model_options': {
            'temperature': 0.7,
            'seed': 42
        }
    }
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config_data, f)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def mock_ollama_available(monkeypatch):
    """Mock Ollama availability check to prevent actual network calls during testing."""
    from unittest.mock import Mock
    from contreact_ollama.llm.ollama_interface import OllamaInterface
    
    original_init = OllamaInterface.__init__
    original_verify = OllamaInterface.verify_model_availability
    
    def mock_init(self, host='http://localhost:11434'):
        self.host = host
        self.client = Mock()
    
    def mock_verify(self, model_name):
        # Mock successful verification
        return True
    
    monkeypatch.setattr(OllamaInterface, '__init__', mock_init)
    monkeypatch.setattr(OllamaInterface, 'verify_model_availability', mock_verify)


def test_full_experiment_run_completes(temp_config_file, mock_ollama_available):
    """Test that a full experiment run completes without errors."""
    # Create ExperimentRunner
    runner = ExperimentRunner(temp_config_file)
    
    # Load configuration
    config = runner.load_config()
    assert config.run_id == 'integration-test-001'
    assert config.cycle_count == 2
    
    # Initialize services
    services = runner.initialize_services()
    assert 'ollama' in services
    
    # Run experiment
    runner.run()  # Should complete without exceptions


def test_experiment_output_shows_cycle_messages(
    temp_config_file, mock_ollama_available, capsys
):
    """Test that experiment output contains expected cycle messages."""
    # Create and run experiment
    runner = ExperimentRunner(temp_config_file)
    runner.run()
    
    # Capture console output
    captured = capsys.readouterr()
    
    # Assert cycle start/finish messages present
    assert "Cycle 1 starting..." in captured.out
    assert "Cycle 1 finished." in captured.out
    assert "Cycle 2 starting..." in captured.out
    assert "Cycle 2 finished." in captured.out
    
    # Assert completion messages present
    assert "✓ Experiment integration-test-001 completed successfully" in captured.out
    assert "✓ Executed 2 cycles" in captured.out


def test_experiment_with_different_cycle_counts(mock_ollama_available):
    """Test experiment execution with various cycle counts."""
    for cycle_count in [1, 3, 5]:
        config_data = {
            'run_id': f'test-{cycle_count}-cycles',
            'model_name': 'llama3:latest',
            'cycle_count': cycle_count,
            'ollama_client_config': {'host': 'http://localhost:11434'},
            'model_options': {'temperature': 0.7}
        }
        
        # Create temporary config
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = f.name
        
        try:
            # Run experiment
            runner = ExperimentRunner(temp_path)
            runner.run()
            # Should complete without errors
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


def test_experiment_runner_stores_config_and_services(
    temp_config_file, mock_ollama_available
):
    """Test that ExperimentRunner properly stores config and services."""
    runner = ExperimentRunner(temp_config_file)
    
    # Initially should not have config or services
    assert not hasattr(runner, 'config')
    assert not hasattr(runner, 'services')
    
    # Load config
    config = runner.load_config()
    
    # Call run which should store config and services
    runner.run()
    
    # After run, should have config and services stored
    assert hasattr(runner, 'config')
    assert hasattr(runner, 'services')
    assert runner.config.run_id == 'integration-test-001'
    assert 'ollama' in runner.services


def test_orchestrator_integration_with_runner(
    temp_config_file, mock_ollama_available, capsys
):
    """Test that CycleOrchestrator integrates correctly with ExperimentRunner."""
    runner = ExperimentRunner(temp_config_file)
    config = runner.load_config()
    services = runner.initialize_services()
    
    # Create orchestrator directly
    orchestrator = CycleOrchestrator(
        config=config,
        ollama_interface=services['ollama']
    )
    
    # Run experiment
    orchestrator.run_experiment()
    
    # Verify output
    captured = capsys.readouterr()
    assert "Starting experiment: integration-test-001" in captured.out
    assert "Model: llama3:latest" in captured.out
    assert "Total cycles: 2" in captured.out


def test_experiment_handles_config_reload(temp_config_file, mock_ollama_available):
    """Test that runner handles multiple config loads gracefully."""
    runner = ExperimentRunner(temp_config_file)
    
    # Load config multiple times
    config1 = runner.load_config()
    config2 = runner.load_config()
    
    # Should return same values
    assert config1.run_id == config2.run_id
    assert config1.cycle_count == config2.cycle_count
    
    # Run should still work
    runner.run()


def test_experiment_runner_with_real_config_file(mock_ollama_available):
    """Test ExperimentRunner with the actual sample config file."""
    config_path = 'configs/sample-config.yaml'
    
    # Check if sample config exists
    if not Path(config_path).exists():
        pytest.skip("Sample config file not found")
    
    # Create runner with real config
    runner = ExperimentRunner(config_path)
    config = runner.load_config()
    
    # Verify config loaded correctly
    assert config.run_id is not None
    assert config.model_name is not None
    assert config.cycle_count > 0
    
    # Initialize services should work
    services = runner.initialize_services()
    assert 'ollama' in services
