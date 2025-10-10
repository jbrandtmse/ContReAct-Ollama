"""Unit tests for OllamaInterface class."""

# Standard library imports
from unittest.mock import Mock, patch

# Third-party imports
import pytest
import ollama

# Local application imports
from contreact_ollama.llm.ollama_interface import OllamaInterface, ModelNotFoundError


@pytest.fixture
def mock_ollama_client():
    """Provide mocked ollama.Client for testing."""
    with patch('ollama.Client') as mock:
        yield mock


def test_init_creates_client_with_default_host(mock_ollama_client):
    """Test that OllamaInterface initializes with default localhost:11434."""
    # Arrange & Act
    interface = OllamaInterface()
    
    # Assert
    mock_ollama_client.assert_called_once_with(host="http://localhost:11434")


def test_init_creates_client_with_custom_host(mock_ollama_client):
    """Test that OllamaInterface initializes with custom host."""
    # Arrange
    custom_host = "http://192.168.0.123:11434"
    
    # Act
    interface = OllamaInterface(host=custom_host)
    
    # Assert
    mock_ollama_client.assert_called_once_with(host=custom_host)


def test_verify_model_availability_model_exists_returns_true(mock_ollama_client):
    """Test that verify_model_availability returns True when model exists."""
    # Arrange
    mock_instance = Mock()
    mock_response = Mock()
    mock_model1 = Mock()
    mock_model1.model = 'llama3:latest'
    mock_model2 = Mock()
    mock_model2.model = 'mistral:latest'
    mock_response.models = [mock_model1, mock_model2]
    mock_instance.list.return_value = mock_response
    mock_ollama_client.return_value = mock_instance
    
    interface = OllamaInterface()
    
    # Act
    result = interface.verify_model_availability('llama3:latest')
    
    # Assert
    assert result is True
    mock_instance.list.assert_called_once()


def test_verify_model_availability_model_not_found_raises_error(mock_ollama_client):
    """Test that verify_model_availability raises ModelNotFoundError when model not found."""
    # Arrange
    mock_instance = Mock()
    mock_response = Mock()
    mock_model1 = Mock()
    mock_model1.model = 'llama3:latest'
    mock_model2 = Mock()
    mock_model2.model = 'mistral:latest'
    mock_response.models = [mock_model1, mock_model2]
    mock_instance.list.return_value = mock_response
    mock_ollama_client.return_value = mock_instance
    
    interface = OllamaInterface()
    
    # Act & Assert
    with pytest.raises(ModelNotFoundError) as exc_info:
        interface.verify_model_availability('nonexistent:latest')
    
    # Verify error message contains helpful instructions
    assert "nonexistent:latest" in str(exc_info.value)
    assert "ollama pull" in str(exc_info.value)


def test_verify_model_availability_connection_error_raises_error(mock_ollama_client):
    """Test that verify_model_availability raises ConnectionError on connection failure."""
    # Arrange
    mock_instance = Mock()
    mock_instance.list.side_effect = ollama.ResponseError("Connection refused")
    mock_ollama_client.return_value = mock_instance
    
    interface = OllamaInterface()
    
    # Act & Assert
    with pytest.raises(ConnectionError) as exc_info:
        interface.verify_model_availability('llama3:latest')
    
    # Verify error message contains helpful instructions
    assert "Failed to connect to Ollama server" in str(exc_info.value)
    assert "ollama serve" in str(exc_info.value)


def test_verify_model_availability_empty_models_list_raises_error(mock_ollama_client):
    """Test that verify_model_availability handles empty models list."""
    # Arrange
    mock_instance = Mock()
    mock_response = Mock()
    mock_response.models = []
    mock_instance.list.return_value = mock_response
    mock_ollama_client.return_value = mock_instance
    
    interface = OllamaInterface()
    
    # Act & Assert
    with pytest.raises(ModelNotFoundError) as exc_info:
        interface.verify_model_availability('llama3:latest')
    
    assert "llama3:latest" in str(exc_info.value)


def test_verify_model_availability_case_sensitive_matching(mock_ollama_client):
    """Test that model name matching is case-sensitive."""
    # Arrange
    mock_instance = Mock()
    mock_response = Mock()
    mock_model = Mock()
    mock_model.model = 'llama3:latest'
    mock_response.models = [mock_model]
    mock_instance.list.return_value = mock_response
    mock_ollama_client.return_value = mock_instance
    
    interface = OllamaInterface()
    
    # Act & Assert - different case should fail
    with pytest.raises(ModelNotFoundError):
        interface.verify_model_availability('LLAMA3:latest')
