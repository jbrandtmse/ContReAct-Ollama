"""
Ollama LLM Interface Module

Provides interface for interacting with local Ollama server for LLM operations.
"""

# Standard library imports
from typing import List, Dict, Any
import json

# Third-party imports
import ollama


class ModelNotFoundError(Exception):
    """Raised when required model is not available locally."""
    pass


class OllamaInterface:
    """
    Interface for communicating with local Ollama LLM server.
    
    This class provides methods for:
    - Verifying model availability
    - Executing chat completions with tool support
    - Managing Ollama client connections
    
    Attributes:
        client: Initialized ollama.Client instance
        
    Example:
        >>> interface = OllamaInterface(host="http://192.168.0.123:11434")
        >>> interface.verify_model_availability("llama3:latest")
        True
    """
    
    def __init__(self, host: str = "http://localhost:11434"):
        """
        Initialize Ollama client with specified host.
        
        Args:
            host: URL of Ollama server (default: http://localhost:11434)
            
        Example:
            >>> interface = OllamaInterface()
            >>> interface = OllamaInterface(host="http://192.168.0.123:11434")
        """
        self.client = ollama.Client(host=host)
        
    def verify_model_availability(self, model_name: str) -> bool:
        """
        Verify model exists locally on Ollama server.
        
        Calls ollama.list() to retrieve available models and checks if the
        requested model is present. Raises error with instructions if not found.
        
        Args:
            model_name: Tag of model to verify (e.g., 'llama3:latest')
            
        Returns:
            True if model is available locally
            
        Raises:
            ConnectionError: If connection to Ollama server fails
            ModelNotFoundError: If model not found locally
            
        Example:
            >>> interface = OllamaInterface()
            >>> interface.verify_model_availability('llama3:latest')
            True
        """
        try:
            # Get list of available models
            response = self.client.list()
            available_models = [model.model for model in response.models]
            
            # Check if requested model is available
            if model_name in available_models:
                return True
            else:
                raise ModelNotFoundError(
                    f"Model '{model_name}' not found locally. "
                    f"Please pull the model first: ollama pull {model_name}"
                )
                
        except ollama.ResponseError as e:
            raise ConnectionError(
                f"Failed to connect to Ollama server: {e}. "
                "Please ensure Ollama is running with: ollama serve"
            )
    
    def execute_chat_completion(
        self,
        model_name: str,
        messages: List[Dict],
        tools: List[Dict],
        options: Dict
    ) -> Dict:
        """
        Execute LLM chat completion.
        
        Args:
            model_name: Tag of model to use (e.g., 'llama3:latest')
            messages: Message history in Ollama chat format
            tools: Tool definitions in JSON schema format
            options: Generation parameters (temperature, seed, etc.)
            
        Returns:
            Dict with 'message' key containing role, content, and optional tool_calls
            
        Raises:
            ollama.ResponseError: On connection or model errors
            
        Example:
            >>> interface = OllamaInterface()
            >>> response = interface.execute_chat_completion(
            ...     model_name="llama3:latest",
            ...     messages=[{"role": "user", "content": "Hello"}],
            ...     tools=[],
            ...     options={"temperature": 0.7}
            ... )
        """
        try:
            response = self.client.chat(
                model=model_name,
                messages=messages,
                tools=tools,
                options=options
            )
            
            # Convert ChatResponse object to dict format
            # The response object has a 'message' attribute with role, content, tool_calls
            message_dict = {
                "role": response.message.role,
                "content": response.message.content or ""
            }
            
            # Include tool_calls if present
            if hasattr(response.message, 'tool_calls') and response.message.tool_calls:
                tool_calls = []
                for tc in response.message.tool_calls:
                    # Sanitize arguments - ensure they're valid JSON
                    # Ollama may return arguments as dict, string, or malformed text
                    arguments = tc.function.arguments
                    
                    # If arguments is a string, validate/sanitize it
                    if isinstance(arguments, str):
                        # Check if it starts with JSON structure indicators
                        stripped = arguments.strip()
                        if not (stripped.startswith('{') or stripped.startswith('[')):
                            # Not JSON at all - model returned raw text
                            print(f"Warning: Tool call '{tc.function.name}' returned non-JSON text instead of arguments")
                            print(f"Raw text: {arguments[:200]}...")  # Show first 200 chars
                            arguments = {}
                        else:
                            try:
                                # Try to parse as JSON to validate
                                parsed_args = json.loads(arguments)
                                arguments = parsed_args
                            except json.JSONDecodeError as e:
                                # If parsing fails, try to sanitize the string
                                # This handles cases where special characters aren't properly escaped
                                print(f"Warning: JSON parsing failed for tool call '{tc.function.name}': {e}")
                                print(f"Raw arguments: {arguments[:200]}...")  # Show first 200 chars
                                
                                # Try to fix common issues
                                try:
                                    # Attempt to clean up the JSON by removing control characters
                                    cleaned = ''.join(char for char in arguments if ord(char) >= 32 or char in '\n\r\t')
                                    parsed_args = json.loads(cleaned)
                                    arguments = parsed_args
                                    print("Successfully cleaned and parsed arguments")
                                except Exception:
                                    # If all else fails, use empty dict
                                    print("Could not recover - using empty arguments")
                                    arguments = {}
                    
                    tool_calls.append({
                        "id": getattr(tc, 'id', None),
                        "function": {
                            "name": tc.function.name,
                            "arguments": arguments
                        }
                    })
                
                message_dict["tool_calls"] = tool_calls
            
            return {"message": message_dict}
            
        except Exception as e:
            raise ollama.ResponseError(f"Error during chat completion: {e}")
