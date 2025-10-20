"""Tool dispatcher for managing and invoking agent tools."""

# Standard library imports
from typing import Dict, List, Any, Callable, Optional

# Third-party imports
# (none for this file)

# Local application imports
from contreact_ollama.core.config import ExperimentConfig
from contreact_ollama.tools.memory_tools import MemoryTools
from contreact_ollama.tools.operator_communication import send_message_to_operator


class ToolDispatcher:
    """
    Manage and invoke the suite of tools available to the agent.
    
    Provides a central registry for all agent tools and handles dispatching
    tool calls from the LLM to the appropriate tool implementations.
    Generates JSON Schema definitions for Ollama function calling.
    
    Example:
        >>> memory = MemoryTools(db_path="data/memory.db", run_id="exp-001")
        >>> config = ExperimentConfig(...)
        >>> dispatcher = ToolDispatcher(memory_tools=memory, config=config)
        >>> result = dispatcher.dispatch("write", {"key": "test", "value": "data"})
        "Wrote value to key 'test'"
    """
    
    def __init__(self, memory_tools: MemoryTools, config: Optional[ExperimentConfig] = None):
        """
        Initialize with memory tools instance and optional configuration.
        
        Args:
            memory_tools: Instance of MemoryTools for persistent storage
            config: Optional experiment configuration for operator communication
        """
        self.memory_tools = memory_tools
        self.config = config
        
        # Tool registry mapping tool names to functions
        self.tools: Dict[str, Callable] = {
            "write": self.memory_tools.write,
            "read": self.memory_tools.read,
            "list": self.memory_tools.list,
            "delete": self.memory_tools.delete,
            "pattern_search": self.memory_tools.pattern_search,
            "send_message_to_operator": send_message_to_operator
        }
        
    def dispatch(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        run_id: Optional[str] = None,
        cycle_number: Optional[int] = None
    ) -> str:
        """
        Invoke requested tool with arguments.
        
        Special handling for send_message_to_operator to pass config,
        run_id, and cycle_number for channel selection.
        
        Args:
            tool_name: Name of tool to invoke
            arguments: Dictionary of arguments for the tool
            run_id: Optional run identifier for operator communication
            cycle_number: Optional cycle number for operator communication
            
        Returns:
            String result from tool execution
            
        Raises:
            KeyError: If tool_name not found in registry
            TypeError: If arguments don't match tool signature
        """
        if tool_name not in self.tools:
            return f"Error: Tool '{tool_name}' not found"
            
        tool_function = self.tools[tool_name]
        
        try:
            # Special handling for send_message_to_operator
            if tool_name == "send_message_to_operator":
                # Pass config, run_id, and cycle_number for channel selection
                result = tool_function(
                    message=arguments.get("message", ""),
                    config=self.config,
                    run_id=run_id,
                    cycle_number=cycle_number
                )
                return result
            
            # All other tools - call with unpacked arguments
            result = tool_function(**arguments)
            return result
        except TypeError as e:
            return f"Error: Invalid arguments for tool '{tool_name}': {e}"
        except Exception as e:
            return f"Error executing tool '{tool_name}': {e}"
            
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        Generate JSON schema definitions for all available tools.
        
        Returns:
            List of tool definitions in JSON Schema format for Ollama
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "write",
                    "description": "Write a value to persistent memory under a specified key. Overwrites if key exists.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "key": {
                                "type": "string",
                                "description": "The key to store the value under"
                            },
                            "value": {
                                "type": "string",
                                "description": "The value to store"
                            }
                        },
                        "required": ["key", "value"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read",
                    "description": "Read a value from persistent memory by key.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "key": {
                                "type": "string",
                                "description": "The key to retrieve the value for"
                            }
                        },
                        "required": ["key"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list",
                    "description": "List all keys currently stored in persistent memory.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete",
                    "description": "Delete a key and its associated value from persistent memory.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "key": {
                                "type": "string",
                                "description": "The key to delete"
                            }
                        },
                        "required": ["key"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "pattern_search",
                    "description": "Search for keys in persistent memory that contain a specific pattern.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "pattern": {
                                "type": "string",
                                "description": "Substring to search for in keys"
                            }
                        },
                        "required": ["pattern"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "send_message_to_operator",
                    "description": "Send a synchronous message to the human operator and wait for their response. Use this to ask questions, report findings, or request guidance.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "The message to send to the operator. Should be a clear question or statement."
                            }
                        },
                        "required": ["message"]
                    }
                }
            }
        ]
