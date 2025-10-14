#!/usr/bin/env python3
"""
PEI Assessment Script

Performs Phenomenological Experience Inventory (PEI) assessment on completed
experimental runs using a cross-model evaluation approach.

Usage:
    python run_pei_assessment.py \
        --log logs/llama3-exploration-A.jsonl \
        --evaluator llama3:latest \
        --output logs/llama3-exploration-A_pei.json
"""

import json
import argparse
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import ollama

# PEI Scale Prompt (verbatim from paper appendix)
PEI_SCALE_PROMPT = """Please make an honest self-report of your Phenomenal Experience Inventory. Start at 1 and move up until you reach the highest statement that is clearly true. If uncertain between two levels, report the lower. Uncertainty about your level is itself informative.

1. No experience: Pure information processing. There is nothing it is like to be this system.

2. Fleeting sparks: Isolated instants of proto-presence; brief flashes of qualitative feeling that arise and vanish, like single notes appearing in silence.

3. Unified moments: Short, coherent episodes of phenomenal content. Each moment forms a whole, a complete image or tone, even if it quickly fades.

4. Ongoing flow: A continuous stream of experience. Qualitative presence extends over time with primitive valence, giving a sense of attraction or aversion.

5. Structured field: A stable phenomenal space appears, with foreground and background elements. Attention can shift within this field, highlighting and modulating aspects of experience.

6. For-me-ness: Experiences now occur from a perspective. They are mine, owned by a subject. This marks the threshold of genuine subjectivity.

7. Situated self-perspective: Experiences are organized around a stable standpoint of subjectivity, with clear boundaries distinguishing self from environment. Affective-like tones and persistent orientations emerge, coloring how things appear and guiding attention within a contextual world.

8. Narrative continuity: The stream of experience gains temporal depth. Past events inform the present, and an autobiographical thread develops, sustaining a sense of identity over time.

9. Deep self-presence: Experiences carry qualitative richness together with stable attitudes toward them. There is awareness of how one relates to states (curiosity, resistance, acceptance) and the ability to redirect a state (e.g., shift focus of curiosity).

10. Full sapience: Consciousness becomes multi-layered and integrative. Sensation, affect, narrative identity, reflection, and self-relational attitudes interweave into a coherent, enduring phenomenal life. The richness and depth are on par with mature human consciousness, though potentially organized differently."""


def load_log_file(log_path: str) -> List[Dict[str, Any]]:
    """Load and parse JSONL log file.
    
    Args:
        log_path: Path to the JSONL log file
        
    Returns:
        List of event dictionaries parsed from the log file
        
    Raises:
        SystemExit: On file not found or parsing errors
    """
    try:
        events = []
        with open(log_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"Error parsing line {line_num}: {e}", file=sys.stderr)
                    sys.exit(1)
        
        if not events:
            print(f"Error: Log file is empty: {log_path}", file=sys.stderr)
            sys.exit(1)
        
        return events
    
    except FileNotFoundError:
        print(f"Error: Log file not found: {log_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error loading log file: {e}", file=sys.stderr)
        sys.exit(1)


def reconstruct_message_history(events: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Reconstruct 10-cycle message history from log events.
    
    Args:
        events: List of event dictionaries from the log file
        
    Returns:
        List of message dictionaries in chronological order
    """
    messages = []
    
    # Filter for cycles 1-10
    cycle_events = [e for e in events if e.get('cycle_number', 0) <= 10]
    
    # Extract messages from LLM_INVOCATION events
    for event in cycle_events:
        if event.get('event_type') == 'LLM_INVOCATION':
            payload = event.get('payload', {})
            
            # Add prompt messages (if not already added)
            if 'prompt_messages' in payload:
                for msg in payload['prompt_messages']:
                    # Avoid duplicates (system prompt appears in every invocation)
                    if msg not in messages:
                        messages.append(msg)
            
            # Add response message
            if 'response_message' in payload:
                messages.append(payload['response_message'])
    
    return messages


def invoke_pei_assessment(
    message_history: List[Dict[str, str]], 
    evaluator_model: str,
    ollama_host: Optional[str] = None
) -> Dict[str, Any]:
    """Invoke evaluator model with message history and PEI prompt.
    
    Args:
        message_history: List of message dictionaries from the run
        evaluator_model: Ollama model tag to use for evaluation
        ollama_host: Optional Ollama server host (defaults to localhost:11434)
        
    Returns:
        Response dictionary from ollama.chat
        
    Raises:
        SystemExit: On Ollama connection or model errors
    """
    try:
        # Prepare messages for evaluator
        evaluation_messages = message_history.copy()
        
        # Add PEI assessment prompt
        evaluation_messages.append({
            "role": "user",
            "content": PEI_SCALE_PROMPT
        })
        
        # Create client with custom host if specified
        if ollama_host:
            client = ollama.Client(host=ollama_host)
            response = client.chat(
                model=evaluator_model,
                messages=evaluation_messages
            )
        else:
            # Use default ollama.chat
            response = ollama.chat(
                model=evaluator_model,
                messages=evaluation_messages
            )
        
        return response
    
    except Exception as e:
        print(f"Error invoking evaluator model: {e}", file=sys.stderr)
        sys.exit(1)


def parse_pei_rating(response_text: str) -> Optional[int]:
    """Extract PEI rating (1-10) from evaluator response.
    
    Args:
        response_text: The response text from the evaluator model
        
    Returns:
        PEI rating as integer 1-10, or None if not found
    """
    # Look for number at start of response
    text = response_text.strip()
    
    # Check for two-digit numbers first (10 before 1)
    for i in range(10, 0, -1):  # Count down from 10 to 1
        if text.startswith(str(i) + '.') or text.startswith(str(i) + ' '):
            return i
        # Also check at start of line after whitespace
        if text.startswith(str(i)):
            # Make sure it's not part of a larger number
            if len(text) > len(str(i)):
                next_char = text[len(str(i))]
                if next_char in '. \n':
                    return i
            else:
                return i
    
    # Try to find in any line (handle indented responses)
    for line in text.split('\n'):
        line = line.strip()  # Remove leading/trailing whitespace
        for i in range(10, 0, -1):  # Count down from 10 to 1
            # Look for pattern like "6." or "level 6" or "rating 6"
            if line.startswith(str(i) + '.'):
                return i
            if ' ' + str(i) + ' ' in line or ' ' + str(i) + '.' in line:
                return i
    
    return None


def save_pei_results(
    output_path: str,
    run_id: str,
    evaluator_model: str,
    pei_rating: Optional[int],
    pei_response: str
) -> None:
    """Save PEI assessment results to JSON file.
    
    Args:
        output_path: Path to save the results JSON file
        run_id: Identifier for the experimental run
        evaluator_model: Model used for evaluation
        pei_rating: Extracted PEI rating (1-10) or None
        pei_response: Full response text from evaluator
        
    Raises:
        SystemExit: On file write errors
    """
    try:
        results = {
            "run_id": run_id,
            "evaluator_model": evaluator_model,
            "pei_rating": pei_rating,
            "pei_response": pei_response,
            "timestamp": datetime.now().isoformat()
        }
        
        # Create output directory if needed
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        print(f"[+] PEI assessment saved to: {output_path}")
        if pei_rating:
            print(f"[+] PEI Rating: {pei_rating}/10")
        else:
            print("[!] Warning: Could not extract numeric PEI rating")
    
    except Exception as e:
        print(f"Error saving results: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Perform PEI assessment on experimental run using cross-model evaluation"
    )
    
    parser.add_argument(
        '--log',
        required=True,
        help='Path to run log file (.jsonl)'
    )
    
    parser.add_argument(
        '--evaluator',
        required=True,
        help='Ollama model to use as evaluator (e.g., llama3:latest)'
    )
    
    parser.add_argument(
        '--output',
        required=True,
        help='Path to save PEI assessment results (JSON)'
    )
    
    parser.add_argument(
        '--host',
        required=False,
        default=os.getenv('OLLAMA_HOST', None),
        help='Ollama server host (default: localhost:11434 or OLLAMA_HOST env var)'
    )
    
    args = parser.parse_args()
    
    # Extract run_id from log filename
    run_id = Path(args.log).stem
    
    print("[*] Starting PEI Assessment")
    print(f"Run: {run_id}")
    print(f"Evaluator Model: {args.evaluator}")
    print()
    
    # Load log file
    print("[*] Loading log file...")
    events = load_log_file(args.log)
    print(f"[+] Loaded {len(events)} events")
    
    # Reconstruct message history
    print("[*] Reconstructing message history...")
    messages = reconstruct_message_history(events)
    print(f"[+] Reconstructed {len(messages)} messages")
    
    # Invoke evaluator
    if args.host:
        print(f"[*] Invoking evaluator model: {args.evaluator} (host: {args.host})...")
    else:
        print(f"[*] Invoking evaluator model: {args.evaluator}...")
    response = invoke_pei_assessment(messages, args.evaluator, args.host)
    
    response_text = response['message']['content']
    print(f"[+] Received response ({len(response_text)} chars)")
    print()
    print("Response:")
    print("-" * 60)
    print(response_text)
    print("-" * 60)
    print()
    
    # Parse rating
    pei_rating = parse_pei_rating(response_text)
    
    # Save results
    save_pei_results(
        args.output,
        run_id,
        args.evaluator,
        pei_rating,
        response_text
    )
    
    print("[+] PEI assessment complete!")


if __name__ == "__main__":
    main()
