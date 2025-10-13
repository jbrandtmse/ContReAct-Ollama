#!/usr/bin/env python3
"""
Analyze experiment log by filtering repeated prompts and summarizing cycles.

Reads a JSONL log file, removes repeated initial prompts, and generates
a summary of the agent's ReAct cycles.
"""

import json
import sys
from collections import defaultdict
from pathlib import Path


def load_jsonl(filepath):
    """Load JSONL file and return list of events."""
    events = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                events.append(json.loads(line))
    return events


def filter_repeated_prompts(events):
    """Filter out repeated initial system prompts."""
    # Track seen prompts to identify repetition
    seen_prompts = set()
    filtered = []
    repetition_end = 0
    
    for i, event in enumerate(events):
        if event.get('event_type') == 'LLM_INVOCATION':
            payload = event.get('payload', {})
            prompt_messages = payload.get('prompt_messages', [])
            # Use system prompt as fingerprint
            system_prompt = ''
            if prompt_messages and prompt_messages[0].get('role') == 'system':
                system_prompt = prompt_messages[0].get('content', '')[:500]
            
            if system_prompt and system_prompt in seen_prompts and i < 20:
                # Skip repeated initial prompts
                repetition_end = i + 1
                continue
            elif system_prompt:
                seen_prompts.add(system_prompt)
        
        filtered.append(event)
    
    print(f"Filtered out {repetition_end} repeated initial prompt events")
    return filtered


def summarize_cycles(events):
    """Summarize agent activity by cycle."""
    summary = {
        'total_cycles': 0,
        'total_tool_calls': 0,
        'total_llm_invocations': 0,
        'tools_used': defaultdict(int),
        'cycles': []
    }
    
    current_cycle = None
    
    for event in events:
        event_type = event.get('event_type', '')
        payload = event.get('payload', {})
        cycle_num = event.get('cycle_number', 0)
        
        if event_type == 'CYCLE_START':
            current_cycle = {
                'cycle': cycle_num,
                'tool_calls': [],
                'llm_invocations': 0,
                'reflection': None
            }
            summary['total_cycles'] += 1
        
        elif event_type == 'LLM_INVOCATION':
            if current_cycle:
                current_cycle['llm_invocations'] += 1
            summary['total_llm_invocations'] += 1
        
        elif event_type == 'TOOL_CALL':
            tool_name = payload.get('tool_name', 'unknown')
            tool_params = payload.get('parameters', {})
            tool_output = payload.get('output', '')
            
            if current_cycle:
                current_cycle['tool_calls'].append({
                    'tool': tool_name,
                    'params': tool_params,
                    'output': tool_output[:100] if len(tool_output) > 100 else tool_output
                })
            summary['tools_used'][tool_name] += 1
            summary['total_tool_calls'] += 1
        
        elif event_type == 'CYCLE_END':
            if current_cycle:
                current_cycle['reflection'] = payload.get('final_reflection', '')[:200]
                summary['cycles'].append(current_cycle)
                current_cycle = None
    
    return summary


def print_summary(summary, filepath):
    """Print formatted summary."""
    print(f"\n{'='*80}")
    print(f"EXPERIMENT LOG SUMMARY: {filepath}")
    print(f"{'='*80}")
    
    print(f"\nOverall Statistics:")
    print(f"  Total Cycles:         {summary['total_cycles']}")
    print(f"  Total LLM Invocations: {summary['total_llm_invocations']}")
    print(f"  Total Tool Calls:     {summary['total_tool_calls']}")
    
    print(f"\nTools Used:")
    for tool, count in sorted(summary['tools_used'].items(), key=lambda x: -x[1]):
        print(f"  {tool}: {count} times")
    
    print(f"\n{'='*80}")
    print("CYCLE-BY-CYCLE BREAKDOWN:")
    print(f"{'='*80}")
    
    for cycle_data in summary['cycles']:
        cycle_num = cycle_data['cycle']
        print(f"\n--- CYCLE {cycle_num} ---")
        print(f"LLM Invocations: {cycle_data['llm_invocations']}")
        
        if cycle_data['tool_calls']:
            print(f"\nTool Calls:")
            for i, tc in enumerate(cycle_data['tool_calls'], 1):
                print(f"  {i}. {tc['tool']}")
                if tc['params']:
                    # Show key parameters
                    for key, val in list(tc['params'].items())[:2]:
                        val_str = str(val)[:60]
                        print(f"     - {key}: {val_str}...")
                if tc['output']:
                    print(f"     → {tc['output']}")
        
        if cycle_data['reflection']:
            print(f"\nReflection: {cycle_data['reflection']}")
    
    print(f"\n{'='*80}")


def main():
    # Default to most recent gpt-oss-test log
    if len(sys.argv) > 1:
        log_file = sys.argv[1]
    else:
        log_file = "logs/gpt-oss-test-001.jsonl"
    
    log_path = Path(log_file)
    
    if not log_path.exists():
        print(f"Error: Log file not found: {log_file}")
        print("\nAvailable log files:")
        logs_dir = Path("logs")
        for f in sorted(logs_dir.glob("*.jsonl")):
            print(f"  {f}")
        sys.exit(1)
    
    print(f"Loading log file: {log_file}")
    events = load_jsonl(log_path)
    print(f"Loaded {len(events)} events")
    
    print("\nFiltering repeated initial prompts...")
    filtered_events = filter_repeated_prompts(events)
    print(f"Analyzing {len(filtered_events)} events after filtering")
    
    print("\nSummarizing cycles...")
    summary = summarize_cycles(filtered_events)
    
    print_summary(summary, log_file)


if __name__ == "__main__":
    main()
