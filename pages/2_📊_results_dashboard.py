"""
Results Dashboard Page

This page allows users to select and analyze completed experiment runs.
Provides run selection, data loading, and displays summary information.

Part of: Story 2.5 - Results Dashboard Run Selector and Data Loading
"""
import streamlit as st
from contreact_ollama.ui_utils import get_log_files, load_log_file


# Page header
st.title("📊 Results Dashboard")

# Run selector section
st.subheader("Select Experiment Run")

log_files = get_log_files()

if log_files:
    selected_log = st.selectbox(
        "Choose a run to analyze",
        options=log_files,
        format_func=lambda x: x.replace('.jsonl', ''),  # Display without extension
        key="selected_run"
    )
    
    # Load selected log with spinner
    if selected_log:
        with st.spinner(f"Loading {selected_log}..."):
            df = load_log_file(selected_log)
        
        if df is not None:
            st.success(f"✅ Loaded {len(df)} events from `{selected_log}`")
            
            # Store in session state for other components
            st.session_state.run_data = df
            st.session_state.current_run = selected_log.replace('.jsonl', '')
            
            # Show basic info
            event_types = df['event_type'].unique() if 'event_type' in df.columns else ['Unknown']
            st.info(f"""
            **Run ID**: {st.session_state.current_run}  
            **Total Events**: {len(df)}  
            **Event Types**: {', '.join(event_types)}
            """)
        else:
            st.error("Failed to load log file. Please check the file format.")
            if 'run_data' in st.session_state:
                del st.session_state.run_data
            if 'current_run' in st.session_state:
                del st.session_state.current_run
else:
    st.info("📭 No experiment logs found.")
    st.markdown("""
    **To get started:**
    1. Create a configuration in the **🧪 Experiment Configuration** page
    2. Run an experiment using the CLI: `python scripts/run_experiment.py --config configs/your-config.yaml`
    3. Return here to view results
    """)

st.divider()

# Placeholder for future components
if 'run_data' in st.session_state:
    st.subheader("Analysis Sections")
    st.info("📊 Summary metrics, charts, and logs will appear here in future stories.")
