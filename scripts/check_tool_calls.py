#!/usr/bin/env python3
"""Check if tool calls are being made."""

import json

log_path = 'logs/qwen-test-fixes-001.jsonl'

with open(log_path, 'r') as f:
    events = [json.loads(line) for line in f]

tool_call_events = [e for e in events if e['event_type'] == 'TOOL_CALL']
invocations = [e for e in events if e['event_type'] == 'LLM_INVOCATION']

print(f"Tool call events logged: {len(tool_call_events)}")
print(f"Total LLM invocations: {len(invocations)}")
print("\nChecking for tool_calls field in responses:")

for i, inv in enumerate(invocations):
    response_msg = inv['payload']['response_message']
    has_tools = 'tool_calls' in response_msg
    print(f"Cycle {i+1}: tool_calls present = {has_tools}")
    if has_tools:
        print(f"  Tool calls: {response_msg['tool_calls']}")
