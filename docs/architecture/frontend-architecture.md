# Frontend Architecture

### Framework and Structure

**Framework**: Streamlit 1.38.0+

**Multi-Page Application Structure**:

```
ui/
├── dashboard.py              # Main entry point
└── pages/
    ├── 1_🧪_Experiment_Configuration.py
    └── 2_📊_Results_Dashboard.py
```

### Component Organization

#### Main Entry Point (dashboard.py)

**Purpose**: Initialize Streamlit app and serve as router

**Key Features**:
- Page configuration (title, icon, layout)
- Sidebar navigation setup
- Theme configuration (light/dark)
- Welcome page content

**Implementation**:
```python
import streamlit as st

st.set_page_config(
    page_title="ContReAct-Ollama Platform",
    page_icon="🧪",
    layout="wide"
)

st.title("ContReAct-Ollama Experimental Platform")
st.markdown("Navigate using the sidebar to configure experiments or view results.")
```

#### Page 1: Experiment Configuration

**File**: `pages/1_🧪_Experiment_Configuration.py`

**Components**:
1. **Configuration Form** (st.form)
   - Text inputs: run_id, model_name, ollama host
   - Number inputs: cycle_count, temperature, seed, top_p, num_predict, etc.
   - Form submit button: "Save Configuration"

2. **Existing Config Loader**
   - Dropdown (st.selectbox) populated by scanning configs/ directory
   - Auto-populate form when config selected
   - Save button overwrites existing file

3. **Validation**
   - Check required fields before save
   - Validate numeric ranges (e.g., temperature 0.0-2.0)
   - Show success/error messages with st.success/st.error

**State Management**: Streamlit session_state for form values

**File System Interface**:
```python
import os
import yaml
from pathlib import Path

# List configs
config_dir = Path("configs")
configs = list(config_dir.glob("*.yaml"))

# Save config
with open(config_dir / f"{run_id}.yaml", 'w') as f:
    yaml.dump(config_dict, f)

# Load config
with open(selected_config, 'r') as f:
    config = yaml.safe_load(f)
```

#### Page 2: Results Dashboard

**File**: `pages/2_📊_Results_Dashboard.py`

**Components**:
1. **Run Selector**
   - Dropdown populated by scanning logs/ directory for .jsonl files
   - Extract run_id from filename

2. **Summary Metrics Display**
   - st.metric widgets for key metrics (memory ops, messages to operator, etc.)
   - st.dataframe for full metrics table

3. **Interactive Charts** (Plotly)
   - Bar chart: Tool calls per cycle
   - Line chart: Response length over cycles
   - Rendered with st.plotly_chart

4. **PEI Results Display** (if available)
   - Check for corresponding PEI assessment file
   - Display in st.dataframe

5. **Raw Log Viewer**
   - st.expander for expandable section
   - Display formatted conversation history

**Data Loading**:
```python
import pandas as pd
import json

# Load log file
with open(log_path, 'r') as f:
    logs = [json.loads(line) for line in f]

# Convert to DataFrame
df = pd.DataFrame(logs)

# Filter by event type
cycle_ends = df[df['event_type'] == 'CYCLE_END']
```

**Chart Creation**:
```python
import plotly.express as px

# Example: Tool calls per cycle
fig = px.bar(
    data, 
    x='cycle_number', 
    y='tool_calls',
    title='Tool Calls Per Cycle'
)
st.plotly_chart(fig)
```

### State Management

**Streamlit Session State**:
- Form input values: `st.session_state.run_id`, etc.
- Selected config: `st.session_state.selected_config`
- Selected run: `st.session_state.selected_run`

**No Global State**: Each page reload reads fresh data from file system

### Routing

**Automatic Streamlit Routing**:
- Files in pages/ directory automatically appear in sidebar
- Numbered prefixes control order (1_, 2_, etc.)
- Emoji prefixes for visual appeal

**Navigation**: Click page name in sidebar

### File System Interface

**Read Operations**:
- List configs: `os.listdir('configs/')`
- Load config: `yaml.safe_load()`
- List runs: `os.listdir('logs/')`
- Load log: Read .jsonl line by line

**Write Operations**:
- Save config: Write YAML to configs/ directory
- No writes to logs/ (read-only for UI)

**Directory Requirements**:
- configs/ must exist (create if missing)
- logs/ must exist (create if missing)

**Error Handling**:
- Check directory existence
- Handle missing files gracefully
- Display user-friendly error messages with st.error()

### Key Design Decisions

1. **Decoupled from Backend**: UI only reads/writes files, never imports backend modules
2. **No Database Connection**: All data via file system
3. **Automatic Refresh**: User manually refreshes page to see new data
4. **Simple State**: Minimal session state, prefer stateless components
5. **Responsive Layout**: Use st.columns for multi-column layouts where needed
