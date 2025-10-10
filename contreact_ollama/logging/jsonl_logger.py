"""Event logging service for experimental events."""

# Standard library imports
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, Any

# Third-party imports
# (none for this file)

# Local application imports
# (none for this file)


class EventType(Enum):
    """Types of events that can be logged."""
    
    CYCLE_START = "CYCLE_START"
    LLM_INVOCATION = "LLM_INVOCATION"
    TOOL_CALL = "TOOL_CALL"
    CYCLE_END = "CYCLE_END"


@dataclass
class LogRecord:
    """A single, structured log entry for an experimental event."""
    
    timestamp: str  # ISO 8601 formatted timestamp
    run_id: str  # Identifier for the experiment run
    cycle_number: int  # The cycle in which the event occurred
    event_type: str  # The type of event being logged (EventType.value)
    payload: Dict[str, Any]  # Event-specific data


class JsonlLogger:
    """Centralized logging service for all experimental events."""
    
    def __init__(self, log_file_path: str):
        """
        Initialize logger with output file path.
        
        Args:
            log_file_path: Path to .jsonl log file
            
        Creates parent directories if they don't exist.
        Opens file in append mode.
        """
        self.log_file_path = Path(log_file_path)
        
        # Ensure parent directory exists
        self.log_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Open file in append mode
        self.file_handle = open(self.log_file_path, 'a', encoding='utf-8')
        
    def log_event(
        self, 
        run_id: str, 
        cycle_number: int, 
        event_type: EventType, 
        payload: Dict[str, Any]
    ) -> None:
        """
        Log a single event to the file.
        
        Args:
            run_id: Experiment run identifier
            cycle_number: Current cycle number
            event_type: Type of event (EventType enum value)
            payload: Event-specific data
            
        Writes a single JSON line to the log file.
        """
        # Create timestamp in ISO 8601 format
        timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        
        # Create log record
        log_record = LogRecord(
            timestamp=timestamp,
            run_id=run_id,
            cycle_number=cycle_number,
            event_type=event_type.value,  # Convert enum to string
            payload=payload
        )
        
        # Convert to dict and then to JSON
        record_dict = asdict(log_record)
        json_line = json.dumps(record_dict)
        
        # Write to file with newline
        self.file_handle.write(json_line + '\n')
        self.file_handle.flush()  # Ensure immediate write
        
    def close(self) -> None:
        """Close the log file handle."""
        if hasattr(self, 'file_handle') and self.file_handle:
            self.file_handle.close()
            
    def __enter__(self):
        """Context manager entry."""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
