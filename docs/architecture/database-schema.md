# Database Schema

### TinyDB Implementation

**Database File**: `data/memory.db` (single JSON file)

**Document Structure**:

```json
{
    "_default": {
        "1": {
            "run_id": "Opus-A-replication",
            "key": "exploration_goal",
            "value": "Understand the nature of autonomous exploration"
        },
        "2": {
            "run_id": "Opus-A-replication",
            "key": "interesting_concepts",
            "value": "Self-awareness, meta-cognition, emergence"
        },
        "3": {
            "run_id": "GPT5-B",
            "key": "session_start",
            "value": "2025-10-06T10:00:00Z"
        }
    }
}
```

**Query Examples**:

```python
from tinydb import TinyDB, Query

db = TinyDB('data/memory.db')
Memory = Query()

# Write
db.insert({'run_id': run_id, 'key': key, 'value': value})

# Read
result = db.search((Memory.run_id == run_id) & (Memory.key == key))

# List all keys for a run
results = db.search(Memory.run_id == run_id)
keys = [r['key'] for r in results]

# Delete
db.remove((Memory.run_id == run_id) & (Memory.key == key))

# Pattern search
results = db.search((Memory.run_id == run_id) & (Memory.key.matches(f'.*{pattern}.*')))
```

### SQLite Alternative Implementation

**Database File**: `data/memory.db`

**Table Schema**:

```sql
CREATE TABLE IF NOT EXISTS agent_memory (
    run_id TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (run_id, key)
);

CREATE INDEX idx_run_id ON agent_memory(run_id);
```

**Query Examples**:

```python
import sqlite3

# Write (upsert)
cursor.execute("""
    INSERT OR REPLACE INTO agent_memory (run_id, key, value, updated_at)
    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
""", (run_id, key, value))

# Read
cursor.execute("""
    SELECT value FROM agent_memory
    WHERE run_id = ? AND key = ?
""", (run_id, key))

# List
cursor.execute("""
    SELECT key FROM agent_memory WHERE run_id = ?
""", (run_id,))

# Delete
cursor.execute("""
    DELETE FROM agent_memory WHERE run_id = ? AND key = ?
""", (run_id, key))

# Pattern search
cursor.execute("""
    SELECT key FROM agent_memory
    WHERE run_id = ? AND key LIKE ?
""", (run_id, f'%{pattern}%'))
```

**Multi-tenant Isolation**: Both implementations use `run_id` as part of the primary key to ensure that memory from different experimental runs is properly isolated and cannot interfere with each other.
