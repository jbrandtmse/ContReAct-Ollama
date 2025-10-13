"""
UI Utilities for Streamlit Dashboard

Provides reusable utility functions for the Streamlit UI pages,
particularly for the Results Dashboard.

Part of: Story 2.5 - Results Dashboard Run Selector and Data Loading
"""
import json
import pandas as pd
import streamlit as st
from pathlib import Path
from typing import Optional


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
