"""
UI Utilities for Streamlit Dashboard

Provides reusable utility functions for the Streamlit UI pages,
particularly for the Results Dashboard.

Part of: Story 2.5 - Results Dashboard Run Selector and Data Loading
Part of: Story 2.6 - Display Summary Metrics on Dashboard
"""
import json
import pandas as pd
import streamlit as st
from pathlib import Path
from typing import Optional, Dict, Any, List


def get_log_files() -> list[str]:
    """
    Scan logs/ directory for .jsonl files.
    
    Returns:
        List of .jsonl filenames sorted by modification time (newest first).
        Returns empty list if directory doesn't exist or contains no .jsonl files.
    """
    logs_dir = Path("logs")
    if not logs_dir.exists():
        return []
    
    jsonl_files = list(logs_dir.glob("*.jsonl"))
    # Sort by modification time (newest first)
    jsonl_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return [f.name for f in jsonl_files]


def load_log_file(filename: str) -> Optional[pd.DataFrame]:
    """
    Load .jsonl log file into DataFrame.
    
    Args:
        filename: Name of the .jsonl file in logs/ directory
        
    Returns:
        DataFrame containing log events, or None if loading fails
    """
    try:
        logs = []
        filepath = Path("logs") / filename
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:  # Skip empty lines
                    continue
                    
                try:
                    logs.append(json.loads(line))
                except json.JSONDecodeError as e:
                    st.error(f"Error parsing line {line_num}: {e}")
                    return None
        
        if not logs:
            st.warning("Log file is empty")
            return None
            
        return pd.DataFrame(logs)
    
    except FileNotFoundError:
        st.error(f"Log file not found: {filename}")
        return None
    except Exception as e:
        st.error(f"Error loading log file: {e}")
        return None


def extract_metrics_from_dataframe(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """
    Extract metrics from CYCLE_END events in log DataFrame.
    
    Args:
        df: DataFrame containing log events
        
    Returns:
        DataFrame with metrics by cycle, or None if no metrics found
    """
    if df is None or 'event_type' not in df.columns:
        return None
    
    # Filter for CYCLE_END events
    cycle_ends = df[df['event_type'] == 'CYCLE_END'].copy()
    
    if len(cycle_ends) == 0:
        return None
    
    # Extract metrics from payload
    metrics_list = []
    for idx, row in cycle_ends.iterrows():
        payload = row['payload']
        if isinstance(payload, dict) and 'metrics' in payload:
            metrics = payload['metrics'].copy()
            metrics['cycle_number'] = row['cycle_number']
            metrics_list.append(metrics)
    
    if not metrics_list:
        return None
    
    return pd.DataFrame(metrics_list)


def calculate_summary_metrics(metrics_df: pd.DataFrame) -> Dict[str, int]:
    """
    Calculate summary totals from metrics DataFrame.
    
    Args:
        metrics_df: DataFrame containing per-cycle metrics
        
    Returns:
        Dictionary with total metrics
    """
    return {
        'total_memory_ops': int(metrics_df['memory_ops_total'].sum()),
        'total_messages': int(metrics_df['messages_to_operator'].sum()),
        'total_response_chars': int(metrics_df['response_chars'].sum()),
        'total_memory_chars': int(metrics_df['memory_write_chars'].sum())
    }


def load_pei_assessment(run_id: str) -> Optional[Dict[str, Any]]:
    """
    Load PEI assessment file for a given run.
    
    Args:
        run_id: Run identifier (without .jsonl extension)
        
    Returns:
        Dictionary containing PEI assessment data, or None if not found
    """
    pei_file = Path(f"logs/{run_id}_pei.json")
    
    if not pei_file.exists():
        return None
    
    try:
        with open(pei_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, Exception):
        return None


def load_memory_entries(run_id: str, db_path: str = "data/memory.db") -> Optional[List[Dict[str, str]]]:
    """
    Load all memory entries for a specific run_id from the TinyDB database.
    
    Args:
        run_id: The experiment run identifier
        db_path: Path to the TinyDB memory database file
        
    Returns:
        List of dictionaries with 'key' and 'value', or None if database doesn't exist
        
    Example:
        >>> entries = load_memory_entries("exp-001")
        >>> for entry in entries:
        ...     print(f"{entry['key']}: {entry['value']}")
    """
    from tinydb import TinyDB, Query
    
    db_file = Path(db_path)
    
    # Check if database file exists
    if not db_file.exists():
        return None
    
    try:
        db = TinyDB(db_file)
        Entry = Query()
        
        # Query all entries for this run_id
        results = db.search(Entry.run_id == run_id)
        
        db.close()
        
        if results:
            # Return list of key-value pairs
            return [{'key': entry['key'], 'value': entry['value']} for entry in results]
        else:
            return []
    
    except Exception as e:
        # Return None on error - UI will display appropriate message
        # Error is logged at UI layer for user visibility
        return None
