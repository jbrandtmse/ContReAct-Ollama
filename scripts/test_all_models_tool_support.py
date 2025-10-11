"""
Test multiple models on the server for Ollama native tool calling support.
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

# Test these models - prioritizing larger/better ones for autonomous behavior
models_to_test = [
    "Plexi09/SentientAI:latest",  # Name suggests autonomous capability
    "gpt-oss:20b",  # Large model
    "jaigouk/nemomix-unleashed-12b:latest",  # 12B model
    "technobyte/fimbulvetr-11b-v2.1-16k:q4_k_m",  # 11B with 16k context
    "technobyte/mn-12b-starcannon-v2:latest",  # 12B model
    "BlackDream/blue-orchid-2x7b:latest",  # MoE model
    "slideshow270/llama-3.1-8b-lexi-uncensored-v2:latest",  # Llama 3.1 variant
    "huihui_ai/Hermes-3-Llama-3.2-abliterated:3b",  # Hermes variant
    "gemma3:4b",  # Google's Gemma
    "llama3.2:3b",  # Already know llama3.1 works
]

results = []

for model_name in models_to_test:
    print(f"\nTesting {model_name}...")
    print("=" * 60)
    
    try:
        client = ollama.Client(host="http://192.168.0.123:11434")
        
        response = client.chat(
            model=model_name,
            messages=messages,
            tools=tools,
            options={"temperature": 0.7}
        )
        
        message = response.message
        has_tool_calls = hasattr(message, 'tool_calls') and message.tool_calls
        
        result = {
            "model": model_name,
            "supports_tools": has_tool_calls,
            "content_length": len(message.content) if message.content else 0,
            "status": "✓ SUPPORTS" if has_tool_calls else "✗ NO SUPPORT"
        }
        results.append(result)
        
        print(f"Tool calls: {result['status']}")
        if has_tool_calls:
            print(f"  Tool: {message.tool_calls[0].function.name}")
        else:
            print(f"  Content length: {result['content_length']}")
            
    except Exception as e:
        print(f"Error: {e}")
        results.append({
            "model": model_name,
            "supports_tools": False,
            "content_length": 0,
            "status": f"ERROR: {str(e)[:50]}"
        })

print("\n\n" + "=" * 60)
print("SUMMARY - Models with Native Tool Calling Support:")
print("=" * 60)

supported = [r for r in results if r["supports_tools"]]
not_supported = [r for r in results if not r["supports_tools"] and "ERROR" not in r["status"]]
errors = [r for r in results if "ERROR" in r["status"]]

if supported:
    print("\n✓ SUPPORTED:")
    for r in supported:
        print(f"  - {r['model']}")
else:
    print("\n✗ No models with native tool calling found")

if not_supported:
    print("\n✗ NOT SUPPORTED:")
    for r in not_supported:
        print(f"  - {r['model']}")

if errors:
    print("\n⚠ ERRORS:")
    for r in errors:
        print(f"  - {r['model']}: {r['status']}")

print("\n" + "=" * 60)
print("RECOMMENDATION:")
if supported:
    print(f"Try using: {supported[0]['model']}")
    print("This model supports native Ollama tool calling.")
else:
    print("None of the tested models support native tool calling.")
    print("Consider:")
    print("  1. Pulling a known tool-calling model like llama3.1:8b")
    print("  2. Modifying the autonomous agent prompt to give initial direction")
    print("  3. Implementing text-based tool parsing for qwen models")
