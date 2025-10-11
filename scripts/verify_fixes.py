#!/usr/bin/env python3
"""Verify that both fixes are working correctly."""

import json
import sys

def verify_fixes(log_path):
    """Verify tool definitions and thinking tag handling."""
    
    # Load all events
    with open(log_path, 'r') as f:
        events = [json.loads(line) for line in f]
    
    invocations = [e for e in events if e['event_type'] == 'LLM_INVOCATION']
    
    print("=" * 80)
    print(f"VERIFICATION REPORT FOR: {log_path}")
    print("=" * 80)
    print(f"\nTotal cycles: {len(invocations)}\n")
    
    # Check Fix 1: Tool definitions in prompt
    print("FIX 1: Tool Definitions in System Prompt")
    print("-" * 80)
    
    cycle1_prompt = invocations[0]['payload']['prompt_messages'][0]['content']
    
    if '## Available Tools' in cycle1_prompt:
        print("✅ PASS: Tool definitions section found in system prompt")
        
        # Extract and show snippet
        tool_start = cycle1_prompt.find('## Available Tools')
        tool_section = cycle1_prompt[tool_start:tool_start+600]
        print("\nSnippet from tool definitions:")
        print(tool_section)
    else:
        print("❌ FAIL: Tool definitions NOT found in system prompt")
    
    # Check Fix 2: Thinking tags handling
    print("\n\nFIX 2: Thinking Tags Handling")
    print("-" * 80)
    
    # Check that thinking IS in the logged response
    cycle1_response = invocations[0]['payload']['response_message']['content']
    has_thinking_in_log = '<thinking>' in cycle1_response
    
    if has_thinking_in_log:
        print("✅ PASS: Thinking tags ARE present in logged response")
        print(f"\nCycle 1 full response (first 300 chars):\n{cycle1_response[:300]}")
    else:
        print("⚠️  WARNING: No thinking tags in Cycle 1 response")
        print(f"Response: {cycle1_response[:200]}")
    
    # Check that thinking is NOT in cycle 2's Previous Reflections
    if len(invocations) > 1:
        cycle2_prompt = invocations[1]['payload']['prompt_messages'][0]['content']
        
        if '## Your Previous Reflections' in cycle2_prompt:
            refl_start = cycle2_prompt.find('## Your Previous Reflections')
            refl_section = cycle2_prompt[refl_start:refl_start+400]
            
            if '<thinking>' not in refl_section:
                print("\n✅ PASS: Thinking tags STRIPPED from Previous Reflections in Cycle 2")
                print(f"\nCycle 2 Previous Reflections snippet:\n{refl_section}")
            else:
                print("\n❌ FAIL: Thinking tags still present in Previous Reflections")
                print(f"\nReflections:\n{refl_section}")
        else:
            print("\n⚠️  No Previous Reflections section in Cycle 2")
    
    print("\n" + "=" * 80)
    print("VERIFICATION COMPLETE")
    print("=" * 80)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python verify_fixes.py <logfile.jsonl>")
        sys.exit(1)
    
    verify_fixes(sys.argv[1])
