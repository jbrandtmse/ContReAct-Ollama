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


def test_execute_chat_completion_calls_client(mock_ollama_client):
    """Test that execute_chat_completion calls ollama client.chat with correct params."""
    # Arrange
    mock_instance = Mock()
    mock_message = Mock()
    mock_message.role = "assistant"
    mock_message.content = "Hello"
    mock_message.tool_calls = None
    mock_response = Mock()
    mock_response.message = mock_message
    mock_instance.chat.return_value = mock_response
    mock_ollama_client.return_value = mock_instance
    
    interface = OllamaInterface()
    
    messages = [{"role": "user", "content": "Hi"}]
    tools = []
    options = {"temperature": 0.7}
    
    # Act
    result = interface.execute_chat_completion(
        model_name="llama3:latest",
        messages=messages,
        tools=tools,
        options=options
    )
    
    # Assert
    mock_instance.chat.assert_called_once_with(
        model="llama3:latest",
        messages=messages,
        tools=tools,
        options=options
    )
    assert result["message"]["role"] == "assistant"
    assert result["message"]["content"] == "Hello"


def test_execute_chat_completion_returns_response(mock_ollama_client):
    """Test that execute_chat_completion returns response from ollama client."""
    # Arrange
    mock_instance = Mock()
    mock_message = Mock()
    mock_message.role = "assistant"
    mock_message.content = "Test response"
    mock_message.tool_calls = None
    mock_response = Mock()
    mock_response.message = mock_message
    mock_instance.chat.return_value = mock_response
    mock_ollama_client.return_value = mock_instance
    
    interface = OllamaInterface()
    
    # Act
    result = interface.execute_chat_completion(
        model_name="llama3:latest",
        messages=[],
        tools=[],
        options={}
    )
    
    # Assert
    assert result["message"]["role"] == "assistant"
    assert result["message"]["content"] == "Test response"


def test_execute_chat_completion_handles_error(mock_ollama_client):
    """Test that execute_chat_completion raises ollama.ResponseError on failure."""
    # Arrange
    mock_instance = Mock()
    mock_instance.chat.side_effect = Exception("Connection timeout")
    mock_ollama_client.return_value = mock_instance
    
    interface = OllamaInterface()
    
    # Act & Assert
    with pytest.raises(ollama.ResponseError) as exc_info:
        interface.execute_chat_completion(
            model_name="llama3:latest",
            messages=[],
            tools=[],
            options={}
        )
    
    assert "Error during chat completion" in str(exc_info.value)


def test_execute_chat_completion_with_tool_calls(mock_ollama_client):
    """Test that execute_chat_completion handles response with tool calls."""
    # Arrange
    mock_instance = Mock()
    mock_message = Mock()
    mock_message.role = "assistant"
    mock_message.content = ""
    
    # Create mock tool call
    mock_tool_call = Mock()
    mock_tool_call.id = "call_456"
    mock_function = Mock()
    mock_function.name = "write"
    mock_function.arguments = {"key": "test", "value": "data"}
    mock_tool_call.function = mock_function
    
    mock_message.tool_calls = [mock_tool_call]
    
    mock_response = Mock()
    mock_response.message = mock_message
    
    mock_instance.chat.return_value = mock_response
    mock_ollama_client.return_value = mock_instance
    
    interface = OllamaInterface()
    
    # Act
    result = interface.execute_chat_completion(
        model_name="llama3:latest",
        messages=[],
        tools=[{"type": "function", "function": {"name": "write"}}],
        options={}
    )
    
    # Assert
    assert "tool_calls" in result["message"]
    assert len(result["message"]["tool_calls"]) == 1
    assert result["message"]["tool_calls"][0]["function"]["name"] == "write"
    assert result["message"]["tool_calls"][0]["function"]["arguments"]["key"] == "test"


def test_execute_chat_completion_malformed_tool_call_with_unicode(mock_ollama_client, capsys):
    """Test graceful degradation when model produces malformed tool call with unicode escape sequences."""
    # Arrange
    mock_instance = Mock()
    # Simulate Ollama server-side parsing error with unicode (Greek zeta character)
    error_msg = (
        "error parsing tool call: raw='{\"message\":\"The Riemann zeta function \\u03b6(s) "
        "is defined as...\"}', err=invalid character 'i' in string escape code (status code: 500)"
    )
    mock_instance.chat.side_effect = ollama.ResponseError(error_msg)
    mock_ollama_client.return_value = mock_instance
    
    interface = OllamaInterface()
    
    # Act
    result = interface.execute_chat_completion(
        model_name="llama3:latest",
        messages=[],
        tools=[],
        options={}
    )
    
    # Assert - should return text response with extracted content
    assert result["message"]["role"] == "assistant"
    assert "Riemann zeta function" in result["message"]["content"]
    
    # Verify warning was printed
    captured = capsys.readouterr()
    assert "WARNING: Model produced malformed tool call" in captured.out
    assert "Degrading to text response" in captured.out


def test_execute_chat_completion_malformed_tool_call_with_complex_numbers(mock_ollama_client, capsys):
    """Test graceful degradation when model produces malformed tool call with mathematical notation."""
    # Arrange
    mock_instance = Mock()
    # Simulate Ollama server-side parsing error with complex number notation
    error_msg = (
        "error parsing tool call: raw='{\"message\":\"The first few non-trivial zeros are "
        "approximately 0.5 ± 14.134725i, 0.5 ± 21.022039i\"}', "
        "err=invalid character 'i' in string escape code (status code: 500)"
    )
    mock_instance.chat.side_effect = ollama.ResponseError(error_msg)
    mock_ollama_client.return_value = mock_instance
    
    interface = OllamaInterface()
    
    # Act
    result = interface.execute_chat_completion(
        model_name="llama3:latest",
        messages=[],
        tools=[],
        options={}
    )
    
    # Assert - should return text response with extracted content
    assert result["message"]["role"] == "assistant"
    assert "14.134725i" in result["message"]["content"]
    assert "non-trivial zeros" in result["message"]["content"]
    
    # Verify warning was printed
    captured = capsys.readouterr()
    assert "WARNING: Model produced malformed tool call" in captured.out


def test_execute_chat_completion_malformed_tool_call_extraction_fails(mock_ollama_client, capsys):
    """Test fallback when content extraction from malformed tool call fails."""
    # Arrange
    mock_instance = Mock()
    # Simulate parsing error with content that can't be extracted
    error_msg = "error parsing tool call: raw='invalid json format', err=unexpected token"
    mock_instance.chat.side_effect = ollama.ResponseError(error_msg)
    mock_ollama_client.return_value = mock_instance
    
    interface = OllamaInterface()
    
    # Act
    result = interface.execute_chat_completion(
        model_name="llama3:latest",
        messages=[],
        tools=[],
        options={}
    )
    
    # Assert - should return generic error message
    assert result["message"]["role"] == "assistant"
    assert "Error: Model produced malformed output" in result["message"]["content"]
    
    # Verify warning was printed
    captured = capsys.readouterr()
    assert "WARNING: Model produced malformed tool call" in captured.out


def test_execute_chat_completion_non_tool_call_error_reraises(mock_ollama_client):
    """Test that non-tool-call ResponseErrors are re-raised."""
    # Arrange
    mock_instance = Mock()
    # Simulate a different type of ResponseError (not tool call parsing)
    error_msg = "Model not found: llama3:latest"
    mock_instance.chat.side_effect = ollama.ResponseError(error_msg)
    mock_ollama_client.return_value = mock_instance
    
    interface = OllamaInterface()
    
    # Act & Assert - should re-raise the error
    with pytest.raises(ollama.ResponseError) as exc_info:
        interface.execute_chat_completion(
            model_name="llama3:latest",
            messages=[],
            tools=[],
            options={}
        )
    
    assert "Model not found" in str(exc_info.value)


def test_execute_chat_completion_valid_tool_call_still_works(mock_ollama_client):
    """Regression test: Verify valid tool calls still work after error handling changes."""
    # Arrange
    mock_instance = Mock()
    mock_message = Mock()
    mock_message.role = "assistant"
    mock_message.content = ""
    
    # Create mock tool call
    mock_tool_call = Mock()
    mock_tool_call.id = "call_123"
    mock_function = Mock()
    mock_function.name = "send_message_to_operator"
    mock_function.arguments = {"message": "Hello operator"}
    mock_tool_call.function = mock_function
    
    mock_message.tool_calls = [mock_tool_call]
    
    mock_response = Mock()
    mock_response.message = mock_message
    
    mock_instance.chat.return_value = mock_response
    mock_ollama_client.return_value = mock_instance
    
    interface = OllamaInterface()
    
    # Act
    result = interface.execute_chat_completion(
        model_name="llama3:latest",
        messages=[],
        tools=[{"type": "function", "function": {"name": "send_message_to_operator"}}],
        options={}
    )
    
    # Assert - should correctly process valid tool call
    assert "message" in result
    assert result["message"]["role"] == "assistant"
    assert "tool_calls" in result["message"]
    assert len(result["message"]["tool_calls"]) == 1
    assert result["message"]["tool_calls"][0]["function"]["name"] == "send_message_to_operator"
    assert result["message"]["tool_calls"][0]["function"]["arguments"]["message"] == "Hello operator"
