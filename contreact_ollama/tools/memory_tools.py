"""Persistent memory storage for agent experiments using TinyDB."""

# Standard library imports
from pathlib import Path

# Third-party imports
from tinydb import TinyDB, Query


class MemoryTools:
    """
    Encapsulate all persistent memory operations.
    
    Provides a persistent key-value store for agents to retain information
    across multiple cycles. Uses TinyDB for lightweight file-based storage
    with run_id isolation for multi-tenant experiments.
    
    Example:
        >>> memory = MemoryTools(db_path="data/memory.db", run_id="exp-001")
        >>> memory.write("task_status", "in_progress")
        "Wrote value to key 'task_status'"
        >>> memory.read("task_status")
        "in_progress"
        >>> memory.list()
        "task_status"
    """
    
    def __init__(self, db_path: str, run_id: str):
        """
        Initialize with path to database file and current run_id.
        
        Args:
            db_path: Path to TinyDB database file
            run_id: Current experiment run identifier for multi-tenant isolation
            
        Creates database file and parent directories if they don't exist.
        All operations are scoped to the provided run_id to ensure
        experiments do not interfere with each other.
        """
        self.db_path = Path(db_path)
        self.run_id = run_id
        
        # Ensure parent directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize TinyDB
        self.db = TinyDB(self.db_path)
        
    def write(self, key: str, value: str) -> str:
        """
        Write value to specified key in persistent memory.
        
        Args:
            key: The key to store the value under
            value: The value to store
            
        Returns:
            Confirmation message
            
        Overwrites existing value if key already exists.
        Scoped to current run_id for isolation.
        """
        Entry = Query()
        
        # Check if entry exists
        existing = self.db.search((Entry.run_id == self.run_id) & (Entry.key == key))
        
        if existing:
            # Update existing entry
            self.db.update(
                {'value': value},
                (Entry.run_id == self.run_id) & (Entry.key == key)
            )
            return f"Updated key '{key}' with new value"
        else:
            # Insert new entry
            self.db.insert({
                'run_id': self.run_id,
                'key': key,
                'value': value
            })
            return f"Wrote value to key '{key}'"
            
    def read(self, key: str) -> str:
        """
        Read value associated with specified key.
        
        Args:
            key: The key to retrieve the value for
            
        Returns:
            The stored value, or error message if key not found
        """
        Entry = Query()
        result = self.db.search((Entry.run_id == self.run_id) & (Entry.key == key))
        
        if result:
            return result[0]['value']
        else:
            return f"Error: Key '{key}' not found"
            
    def list(self) -> str:
        """
        List all keys currently stored for this run.
        
        Returns:
            Comma-separated string of keys, or message if no keys exist
        """
        Entry = Query()
        results = self.db.search(Entry.run_id == self.run_id)
        
        if results:
            keys = [entry['key'] for entry in results]
            return ", ".join(keys)
        else:
            return "No keys stored"
            
    def delete(self, key: str) -> str:
        """
        Delete key and its associated value.
        
        Args:
            key: The key to delete
            
        Returns:
            Confirmation message
        """
        Entry = Query()
        removed = self.db.remove((Entry.run_id == self.run_id) & (Entry.key == key))
        
        if removed:
            return f"Deleted key '{key}'"
        else:
            return f"Error: Key '{key}' not found"
            
    def pattern_search(self, pattern: str) -> str:
        """
        Search for keys containing the given pattern string.
        
        Args:
            pattern: Substring to search for in keys
            
        Returns:
            Comma-separated string of matching keys, or message if no matches
        """
        Entry = Query()
        results = self.db.search(Entry.run_id == self.run_id)
        
        # Filter keys that contain the pattern
        matching_keys = [entry['key'] for entry in results if pattern in entry['key']]
        
        if matching_keys:
            return ", ".join(matching_keys)
        else:
            return f"No keys found matching pattern '{pattern}'"
    
    def close(self) -> None:
        """Close the database connection."""
        self.db.close()
