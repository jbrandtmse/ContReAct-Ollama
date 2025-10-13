"""
Test all available models on Ollama server for tool calling support.

This script:
1. Discovers all models available on the Ollama server
2. Tests each model for tool calling compatibility
3. Reports which models work with ContReAct experiments
"""

import ollama
import sys
from typing import List, Dict, Tuple

# Ollama server configuration
OLLAMA_HOST = "http://192.168.0.123:11434"

# Simple tool definition for testing
TEST_TOOLS = [
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
TEST_MESSAGES = [
    {
        "role": "user",
        "content": "What's the weather in San Francisco?"
    }
]


def get_all_models(client: ollama.Client) -> List[Dict]:
    """
    Retrieve all available models from Ollama server.
    
    Returns:
        List of model dictionaries with 'name' and 'size' fields
    """
    try:
        response = client.list()
        models = []
        for model in response.models:
            models.append({
                'name': model.model,
                'size': model.size if hasattr(model, 'size') else 'unknown'
            })
        return models
    except Exception as e:
        print(f"Error listing models: {e}")
        return []


def format_size(size_bytes: int) -> str:
    """Convert bytes to human-readable size."""
    if isinstance(size_bytes, str):
        return size_bytes
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def test_model_tool_support(client: ollama.Client, model_name: str) -> Tuple[bool, str]:
    """
    Test if a model supports tool calling.
    
    Args:
        client: Ollama client instance
        model_name: Name of model to test
        
    Returns:
        Tuple of (supports_tools: bool, message: str)
    """
    try:
        # Attempt to call model with tools parameter
        response = client.chat(
            model=model_name,
            messages=TEST_MESSAGES,
            tools=TEST_TOOLS,
            options={'num_predict': 100}  # Limit response length for speed
        )
        
        # Check if response contains structured tool_calls
        message = response.message
        if hasattr(message, 'tool_calls') and message.tool_calls:
            # Model returned structured tool calls - it supports tools!
            return True, "✓ Returns structured tool_calls"
        else:
            # Model accepted tools parameter but didn't return tool_calls
            return False, "✗ No tool_calls in response (text only)"
            
    except ollama.ResponseError as e:
        error_msg = str(e)
        
        # Check for specific error messages
        if "does not support tools" in error_msg.lower():
            return False, "✗ Model does not support tools (Ollama rejection)"
        elif "status code: 400" in error_msg:
            return False, "✗ HTTP 400 - Model incompatible with tools"
        elif "status code: 404" in error_msg:
            return False, "✗ Model not found"
        else:
            return False, f"✗ Error: {error_msg[:60]}..."
            
    except Exception as e:
        return False, f"✗ Unexpected error: {str(e)[:60]}..."


def main():
    """Main execution function."""
    print("=" * 80)
    print("ContReAct Tool Calling Compatibility Test")
    print("=" * 80)
    print(f"\nConnecting to Ollama server at {OLLAMA_HOST}...")
    
    try:
        client = ollama.Client(host=OLLAMA_HOST)
        
        # Verify connection
        models = get_all_models(client)
        
        if not models:
            print("✗ No models found or unable to connect to Ollama server")
            print(f"\nPlease ensure Ollama is running at {OLLAMA_HOST}")
            sys.exit(1)
            
        print(f"✓ Connected successfully")
        print(f"✓ Found {len(models)} model(s) to test\n")
        
        # Test each model
        results = {
            'compatible': [],
            'incompatible': []
        }
        
        print("Testing models for tool calling support...")
        print("-" * 80)
        
        for i, model_info in enumerate(models, 1):
            model_name = model_info['name']
            model_size = format_size(model_info['size'])
            
            print(f"\n[{i}/{len(models)}] Testing: {model_name} ({model_size})")
            
            supports_tools, message = test_model_tool_support(client, model_name)
            
            print(f"    {message}")
            
            if supports_tools:
                results['compatible'].append(model_name)
            else:
                results['incompatible'].append(model_name)
        
        # Print summary
        print("\n" + "=" * 80)
        print("SUMMARY REPORT")
        print("=" * 80)
        
        print(f"\n✓ COMPATIBLE MODELS ({len(results['compatible'])} total):")
        print("These models work with ContReAct experiments:\n")
        if results['compatible']:
            for model in results['compatible']:
                print(f"  • {model}")
        else:
            print("  (none found)")
        
        print(f"\n✗ INCOMPATIBLE MODELS ({len(results['incompatible'])} total):")
        print("These models cannot be used with ContReAct:\n")
        if results['incompatible']:
            for model in results['incompatible']:
                print(f"  • {model}")
        else:
            print("  (none found)")
        
        # Recommendations
        print("\n" + "=" * 80)
        print("RECOMMENDATIONS")
        print("=" * 80)
        
        if results['compatible']:
            print(f"\nUse one of the {len(results['compatible'])} compatible model(s) for your experiments.")
            print("\nExample configuration:")
            print(f"""
run_id: "experiment-001"
model_name: "{results['compatible'][0]}"
cycle_count: 10
""")
        else:
            print("\n⚠ No compatible models found!")
            print("\nTo use ContReAct, you need models that support Ollama's native tool calling.")
            print("\nRecommended models to pull:")
            print("  • ollama pull llama3.1:8b")
            print("  • ollama pull qwen2.5:7b")
            print("  • ollama pull gpt-oss:20b")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
