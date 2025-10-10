# Standard library imports
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

# Third-party imports
import pytest
import yaml
import ollama

# Local application imports
from contreact_ollama.core.experiment_runner import ExperimentRunner
from contreact_ollama.core.config import ExperimentConfig
from contreact_ollama.llm.ollama_interface import ModelNotFoundError


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
    
    @patch('contreact_ollama.llm.ollama_interface.ollama.Client')
    def test_initialize_services_with_valid_model_succeeds(self, mock_ollama_client):
        """Test that initialize_services succeeds with valid model."""
        # Arrange
        config_data = {
            'run_id': 'test-run',
            'model_name': 'llama3:latest',
            'cycle_count': 5,
            'ollama_client_config': {'host': 'http://192.168.0.123:11434'},
            'model_options': {'temperature': 0.8}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = f.name
        
        # Mock ollama client to return available models
        mock_instance = Mock()
        mock_response = Mock()
        mock_model1 = Mock()
        mock_model1.model = 'llama3:latest'
        mock_model2 = Mock()
        mock_model2.model = 'mistral:latest'
        mock_response.models = [mock_model1, mock_model2]
        mock_instance.list.return_value = mock_response
        mock_ollama_client.return_value = mock_instance
        
        try:
            runner = ExperimentRunner(temp_path)
            
            # Act
            services = runner.initialize_services()
            
            # Assert
            assert 'ollama' in services
            assert services['ollama'] is not None
            mock_ollama_client.assert_called_once_with(host='http://192.168.0.123:11434')
            mock_instance.list.assert_called_once()
        finally:
            Path(temp_path).unlink()
    
    @patch('contreact_ollama.llm.ollama_interface.ollama.Client')
    def test_initialize_services_with_invalid_model_raises_error(self, mock_ollama_client):
        """Test that initialize_services raises ModelNotFoundError for unavailable model."""
        # Arrange
        config_data = {
            'run_id': 'test-run',
            'model_name': 'nonexistent:latest',
            'cycle_count': 5,
            'ollama_client_config': {'host': 'http://192.168.0.123:11434'},
            'model_options': {'temperature': 0.8}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = f.name
        
        # Mock ollama client to return available models (not including nonexistent)
        mock_instance = Mock()
        mock_response = Mock()
        mock_model1 = Mock()
        mock_model1.model = 'llama3:latest'
        mock_model2 = Mock()
        mock_model2.model = 'mistral:latest'
        mock_response.models = [mock_model1, mock_model2]
        mock_instance.list.return_value = mock_response
        mock_ollama_client.return_value = mock_instance
        
        try:
            runner = ExperimentRunner(temp_path)
            
            # Act & Assert
            with pytest.raises(ModelNotFoundError) as exc_info:
                runner.initialize_services()
            
            assert 'nonexistent:latest' in str(exc_info.value)
            assert 'ollama pull' in str(exc_info.value)
        finally:
            Path(temp_path).unlink()
    
    @patch('contreact_ollama.llm.ollama_interface.ollama.Client')
    def test_initialize_services_connection_error_raises_error(self, mock_ollama_client):
        """Test that initialize_services raises ConnectionError on Ollama connection failure."""
        # Arrange
        config_data = {
            'run_id': 'test-run',
            'model_name': 'llama3:latest',
            'cycle_count': 5,
            'ollama_client_config': {'host': 'http://192.168.0.123:11434'},
            'model_options': {'temperature': 0.8}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = f.name
        
        # Mock ollama client to raise ResponseError
        mock_instance = Mock()
        mock_instance.list.side_effect = ollama.ResponseError("Connection refused")
        mock_ollama_client.return_value = mock_instance
        
        try:
            runner = ExperimentRunner(temp_path)
            
            # Act & Assert
            with pytest.raises(ConnectionError) as exc_info:
                runner.initialize_services()
            
            assert 'Failed to connect to Ollama server' in str(exc_info.value)
        finally:
            Path(temp_path).unlink()
    
    @patch('contreact_ollama.llm.ollama_interface.ollama.Client')
    def test_initialize_services_uses_default_host_when_not_specified(self, mock_ollama_client):
        """Test that initialize_services uses default host when not in config."""
        # Arrange
        config_data = {
            'run_id': 'test-run',
            'model_name': 'llama3:latest',
            'cycle_count': 5,
            'ollama_client_config': {},  # No host specified
            'model_options': {'temperature': 0.8}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = f.name
        
        # Mock ollama client
        mock_instance = Mock()
        mock_response = Mock()
        mock_model = Mock()
        mock_model.model = 'llama3:latest'
        mock_response.models = [mock_model]
        mock_instance.list.return_value = mock_response
        mock_ollama_client.return_value = mock_instance
        
        try:
            runner = ExperimentRunner(temp_path)
            
            # Act
            services = runner.initialize_services()
            
            # Assert - should use default localhost
            mock_ollama_client.assert_called_once_with(host='http://localhost:11434')
        finally:
            Path(temp_path).unlink()
