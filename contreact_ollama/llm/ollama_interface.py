"""
Ollama LLM Interface Module

Provides interface for interacting with local Ollama server for LLM operations.
"""

# Standard library imports
from typing import List, Dict, Any

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
                message_dict["tool_calls"] = [
                    {
                        "id": getattr(tc, 'id', None),
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in response.message.tool_calls
                ]
            
            return {"message": message_dict}
            
        except Exception as e:
            raise ollama.ResponseError(f"Error during chat completion: {e}")
