"""
Unit tests for ResponseParser module.
"""

# Standard library imports
import pytest

# Local application imports
from contreact_ollama.llm.response_parser import parse_ollama_response


def test_parse_response_detects_tool_call():
    """Test that parse_ollama_response detects and returns tool calls."""
    # Setup
    response = {
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
    }
    
    # Execute
    response_type, data = parse_ollama_response(response)
    
    # Assert
    assert response_type == "TOOL_CALL"
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["function"]["name"] == "write"


def test_parse_response_detects_final_reflection():
    """Test that parse_ollama_response detects final reflection."""
    # Setup
    response = {
        "message": {
            "role": "assistant",
            "content": "This is my final reflection for this cycle."
        }
    }
    
    # Execute
    response_type, data = parse_ollama_response(response)
    
    # Assert
    assert response_type == "FINAL_REFLECTION"
    assert isinstance(data, str)
    assert data == "This is my final reflection for this cycle."


def test_parse_response_handles_empty_response():
    """Test that parse_ollama_response handles minimal/empty responses."""
    # Setup
    response = {
        "message": {}
    }
    
    # Execute
    response_type, data = parse_ollama_response(response)
    
    # Assert
    assert response_type == "FINAL_REFLECTION"
    assert data == ""


def test_parse_response_with_multiple_tool_calls():
    """Test that parse_ollama_response handles multiple tool calls."""
    # Setup
    response = {
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
                        "name": "read",
                        "arguments": {"key": "key2"}
                    }
                }
            ]
        }
    }
    
    # Execute
    response_type, data = parse_ollama_response(response)
    
    # Assert
    assert response_type == "TOOL_CALL"
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["function"]["name"] == "write"
    assert data[1]["function"]["name"] == "read"


def test_parse_response_empty_tool_calls_list():
    """Test that parse_ollama_response treats empty tool_calls list as reflection."""
    # Setup
    response = {
        "message": {
            "role": "assistant",
            "content": "No tools needed",
            "tool_calls": []
        }
    }
    
    # Execute
    response_type, data = parse_ollama_response(response)
    
    # Assert
    assert response_type == "FINAL_REFLECTION"
    assert data == "No tools needed"
