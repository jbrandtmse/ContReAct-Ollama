"""
Test if models support Ollama native tool calling.
"""

import ollama

# Simple tool definition
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city name"
                    }
                },
                "required": ["city"]
            }
        }
    }
]

# Test message that should trigger tool use
messages = [
    {
        "role": "user",
        "content": "What's the weather in San Francisco?"
    }
]

# Test multiple models
models_to_test = [
    "llama3.1:8b",
    "maryasov/llama3.1-cline:latest"
]

for model_name in models_to_test:
    print(f"\nTesting {model_name} tool calling support...")
    print("=" * 60)
    
    try:
        client = ollama.Client(host="http://192.168.0.123:11434")
        
        response = client.chat(
            model=model_name,
            messages=messages,
            tools=tools
        )
        
        print("\nResponse structure:")
        print(f"Type: {type(response)}")
        
        print("\nMessage content:")
        message = response.message
        print(f"Role: {message.role}")
        print(f"Content: {message.content[:200] if message.content else 'None'}...")
        
        print("\nTool calls:")
        if hasattr(message, 'tool_calls') and message.tool_calls:
            print(f"✓ Model returned tool_calls field")
            print(f"Tool calls: {message.tool_calls}")
        else:
            print(f"✗ No tool_calls field in response")
            print(f"Model returned only text content (not structured tool calls)")
            
        print("\n" + "=" * 60)
        
        if hasattr(message, 'tool_calls') and message.tool_calls:
            print(f"RESULT: {model_name} SUPPORTS native tool calling ✓")
        else:
            print(f"RESULT: {model_name} DOES NOT support native tool calling ✗")
            
    except Exception as e:
        print(f"\nError testing {model_name}: {e}")
        print("=" * 60)

print("\n\nSUMMARY: Use a model that supports native tool calling for ContReAct experiments.")
