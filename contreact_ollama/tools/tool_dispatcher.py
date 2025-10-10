"""Tool dispatcher for managing and invoking agent tools."""

# Standard library imports
from typing import Dict, List, Any, Callable

# Third-party imports
# (none for this file)

# Local application imports
from contreact_ollama.tools.memory_tools import MemoryTools


class ToolDispatcher:
    """
    Manage and invoke the suite of tools available to the agent.
    
    Provides a central registry for all agent tools and handles dispatching
    tool calls from the LLM to the appropriate tool implementations.
    Generates JSON Schema definitions for Ollama function calling.
    
    Example:
        >>> memory = MemoryTools(db_path="data/memory.db", run_id="exp-001")
        >>> dispatcher = ToolDispatcher(memory_tools=memory)
        >>> result = dispatcher.dispatch("write", {"key": "test", "value": "data"})
        "Wrote value to key 'test'"
    """
    
    def __init__(self, memory_tools: MemoryTools):
        """
        Initialize with memory tools instance.
        
        Args:
            memory_tools: Instance of MemoryTools for persistent storage
            
        Note:
            send_message_to_operator will be added in Story 1.7
        """
        self.memory_tools = memory_tools
        
        # Tool registry mapping tool names to functions
        self.tools: Dict[str, Callable] = {
            "write": self.memory_tools.write,
            "read": self.memory_tools.read,
            "list": self.memory_tools.list,
            "delete": self.memory_tools.delete,
            "pattern_search": self.memory_tools.pattern_search,
            # send_message_to_operator will be added in Story 1.7
        }
        
    def dispatch(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        Invoke requested tool with arguments.
        
        Args:
            tool_name: Name of tool to invoke
            arguments: Dictionary of arguments for the tool
            
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
            # Call tool with unpacked arguments
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
            }
        ]
