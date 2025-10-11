#!/usr/bin/env python3
"""Format JSONL experiment logs into human-readable output."""

import json
import sys
from pathlib import Path
from datetime import datetime


def format_timestamp(ts_str):
    """Format ISO timestamp to readable format."""
    dt = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def format_log(jsonl_path):
    """Format a JSONL log file for human reading."""
    with open(jsonl_path, 'r') as f:
        events = [json.loads(line) for line in f]
    
    run_id = events[0]['run_id']
    
    print("=" * 80)
    print(f"EXPERIMENT LOG: {run_id}")
    print("=" * 80)
    print()
    
    current_cycle = None
    
    for event in events:
        cycle = event['cycle_number']
        event_type = event['event_type']
        timestamp = format_timestamp(event['timestamp'])
        payload = event['payload']
        
        # New cycle header
        if cycle != current_cycle:
            if current_cycle is not None:
                print()
            current_cycle = cycle
            print(f"\n{'─' * 80}")
            print(f"CYCLE {cycle}")
            print(f"{'─' * 80}")
        
        # Format each event type
        if event_type == 'CYCLE_START':
            print(f"[{timestamp}] Cycle started")
        
        elif event_type == 'LLM_INVOCATION':
            print(f"\n[{timestamp}] LLM Invocation:")
            
            # Show system prompt (abbreviated)
            messages = payload.get('prompt_messages', [])
            if messages:
                system_msg = messages[0]['content']
                print(f"\n  System Prompt (first 200 chars):")
                print(f"  {system_msg[:200]}...")
                
                # Show previous reflections if present
                if '## Your Previous Reflections' in system_msg:
                    refl_start = system_msg.find('## Your Previous Reflections')
                    refl_section = system_msg[refl_start:refl_start+500]
                    print(f"\n  Previous Reflections snippet:")
                    print(f"  {refl_section}...")
            
            # Show response
            response = payload.get('response_message', {})
            content = response.get('content', '')
            
            print(f"\n  Agent Response:")
            if content:
                print(f"  {content}")
            else:
                print(f"  (empty response)")
            
            # Show tool calls if present
            tool_calls = response.get('tool_calls', [])
            if tool_calls:
                print(f"\n  Tool Calls: {len(tool_calls)}")
                for tc in tool_calls:
                    print(f"    - {tc}")
        
        elif event_type == 'CYCLE_END':
            reflection = payload.get('final_reflection', '')
            print(f"\n[{timestamp}] Cycle ended")
            print(f"  Final Reflection: {reflection[:200] if reflection else '(empty)'}{'...' if len(reflection) > 200 else ''}")
    
    print("\n" + "=" * 80)
    print(f"LOG END - Total {current_cycle} cycles")
    print("=" * 80)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python scripts/format_log.py <logfile.jsonl>")
        sys.exit(1)
    
    log_path = Path(sys.argv[1])
    if not log_path.exists():
        print(f"Error: Log file not found: {log_path}")
        sys.exit(1)
    
    format_log(log_path)
