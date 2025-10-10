# Standard library imports
import tempfile
from pathlib import Path

# Third-party imports
import pytest
import yaml

# Local application imports
from contreact_ollama.core.experiment_runner import ExperimentRunner
from contreact_ollama.core.config import ExperimentConfig


class TestExperimentRunner:
    """Unit tests for ExperimentRunner class."""
    
    def test_load_config_valid_file_returns_config(self):
        """Test that load_config returns ExperimentConfig with valid file."""
        # Create temporary valid config file
        config_data = {
            'run_id': 'test-run-001',
            'model_name': 'llama3:latest',
            'cycle_count': 5,
            'ollama_client_config': {'host': 'http://localhost:11434'},
            'model_options': {'temperature': 0.8, 'seed': 123}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = f.name
        
        try:
            # Load config
            runner = ExperimentRunner(temp_path)
            config = runner.load_config()
            
            # Assert correct values
            assert isinstance(config, ExperimentConfig)
            assert config.run_id == 'test-run-001'
            assert config.model_name == 'llama3:latest'
            assert config.cycle_count == 5
            assert config.ollama_client_config == {'host': 'http://localhost:11434'}
            assert config.model_options == {'temperature': 0.8, 'seed': 123}
        finally:
            Path(temp_path).unlink()
    
    def test_load_config_missing_file_raises_error(self):
        """Test that load_config raises FileNotFoundError for non-existent file."""
        runner = ExperimentRunner('nonexistent-file.yaml')
        
        with pytest.raises(FileNotFoundError) as exc_info:
            runner.load_config()
        
        assert 'Configuration file not found' in str(exc_info.value)
        assert 'nonexistent-file.yaml' in str(exc_info.value)
    
    def test_load_config_invalid_yaml_raises_error(self):
        """Test that load_config raises yaml.YAMLError for malformed YAML."""
        # Create temporary file with invalid YAML
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: [unclosed bracket")
            temp_path = f.name
        
        try:
            runner = ExperimentRunner(temp_path)
            
            with pytest.raises(yaml.YAMLError) as exc_info:
                runner.load_config()
            
            assert 'Invalid YAML syntax' in str(exc_info.value)
        finally:
            Path(temp_path).unlink()
    
    def test_load_config_missing_required_field_raises_error(self):
        """Test that load_config raises KeyError when required field is missing."""
        # Create config missing 'run_id' field
        config_data = {
            'model_name': 'llama3:latest',
            'cycle_count': 5,
            'ollama_client_config': {'host': 'http://localhost:11434'},
            'model_options': {'temperature': 0.8}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = f.name
        
        try:
            runner = ExperimentRunner(temp_path)
            
            with pytest.raises(KeyError) as exc_info:
                runner.load_config()
            
            assert 'Missing required field' in str(exc_info.value)
            assert 'run_id' in str(exc_info.value)
        finally:
            Path(temp_path).unlink()
    
    def test_load_config_invalid_field_type_raises_error(self):
        """Test that load_config raises TypeError for invalid field type."""
        # Create config with cycle_count as string instead of int
        config_data = {
            'run_id': 'test-run',
            'model_name': 'llama3:latest',
            'cycle_count': 'ten',  # Should be int
            'ollama_client_config': {'host': 'http://localhost:11434'},
            'model_options': {'temperature': 0.8}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = f.name
        
        try:
            runner = ExperimentRunner(temp_path)
            
            with pytest.raises(TypeError) as exc_info:
                runner.load_config()
            
            assert 'Invalid value for field' in str(exc_info.value)
            assert 'cycle_count' in str(exc_info.value)
        finally:
            Path(temp_path).unlink()
    
    def test_load_config_invalid_cycle_count_raises_error(self):
        """Test that load_config raises ValueError for cycle_count <= 0."""
        # Create config with cycle_count = 0
        config_data = {
            'run_id': 'test-run',
            'model_name': 'llama3:latest',
            'cycle_count': 0,  # Should be > 0
            'ollama_client_config': {'host': 'http://localhost:11434'},
            'model_options': {'temperature': 0.8}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = f.name
        
        try:
            runner = ExperimentRunner(temp_path)
            
            with pytest.raises(ValueError) as exc_info:
                runner.load_config()
            
            assert 'cycle_count' in str(exc_info.value)
            assert 'greater than 0' in str(exc_info.value)
        finally:
            Path(temp_path).unlink()
