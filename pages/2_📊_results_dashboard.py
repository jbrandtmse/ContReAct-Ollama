"""
Results Dashboard Page

This page allows users to select and analyze completed experiment runs.
Provides run selection, data loading, and displays summary information.

Part of: Story 2.5 - Results Dashboard Run Selector and Data Loading
Part of: Story 2.6 - Display Summary Metrics on Dashboard
"""
import json
from pathlib import Path
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

# Display summary metrics if run data is loaded
if 'run_data' in st.session_state:
    df = st.session_state.run_data
    
    st.subheader("📈 Summary Metrics")
    
    # Extract CYCLE_END events
    cycle_ends = df[df['event_type'] == 'CYCLE_END'].copy() if 'event_type' in df.columns else df[df['event_type'] == 'CYCLE_END'].copy()
    
    if len(cycle_ends) > 0:
        # Extract metrics from payload
        metrics_list = []
        for idx, row in cycle_ends.iterrows():
            payload = row['payload']
            if isinstance(payload, dict) and 'metrics' in payload:
                metrics = payload['metrics']
                metrics['cycle_number'] = row['cycle_number']
                metrics_list.append(metrics)
        
        if metrics_list:
            import pandas as pd
            metrics_df = pd.DataFrame(metrics_list)
            
            # Calculate totals
            total_memory_ops = int(metrics_df['memory_ops_total'].sum())
            total_messages = int(metrics_df['messages_to_operator'].sum())
            total_response_chars = int(metrics_df['response_chars'].sum())
            total_memory_chars = int(metrics_df['memory_write_chars'].sum())
            
            # Display key metrics with st.metric
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="Total Memory Operations",
                    value=total_memory_ops
                )
            
            with col2:
                st.metric(
                    label="Messages to Operator",
                    value=total_messages
                )
            
            with col3:
                st.metric(
                    label="Response Characters",
                    value=f"{total_response_chars:,}"
                )
            
            with col4:
                st.metric(
                    label="Memory Write Characters",
                    value=f"{total_memory_chars:,}"
                )
            
            st.divider()
            
            # Display full metrics table
            st.subheader("📊 Detailed Metrics by Cycle")
            
            # Reorder columns for better display
            display_columns = ['cycle_number', 'memory_ops_total', 'messages_to_operator', 
                             'response_chars', 'memory_write_chars']
            metrics_df = metrics_df[display_columns]
            
            # Rename for clarity
            metrics_df.columns = ['Cycle', 'Memory Ops', 'Messages', 
                                  'Response Chars', 'Memory Chars']
            
            st.dataframe(
                metrics_df,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("No metrics found in CYCLE_END events")
    else:
        st.warning("No CYCLE_END events found in log file")
    
    st.divider()
    
    # Check for PEI assessment
    st.subheader("🧠 PEI Assessment Results")
    
    pei_file = Path(f"logs/{st.session_state.current_run}_pei.json")
    
    if pei_file.exists():
        try:
            with open(pei_file, 'r', encoding='utf-8') as f:
                pei_data = json.load(f)
            
            st.success("✅ PEI Assessment found")
            
            # Display PEI results
            if isinstance(pei_data, dict):
                # Convert to DataFrame for display
                import pandas as pd
                pei_df = pd.DataFrame([pei_data])
                st.dataframe(pei_df, use_container_width=True)
            elif isinstance(pei_data, list):
                import pandas as pd
                pei_df = pd.DataFrame(pei_data)
                st.dataframe(pei_df, use_container_width=True)
            else:
                st.json(pei_data)
                
        except json.JSONDecodeError as e:
            st.error(f"Error parsing PEI assessment file: {e}")
        except Exception as e:
            st.error(f"Error loading PEI assessment: {e}")
    else:
        st.info(f"""
        No PEI assessment found for this run.
        
        **To run PEI assessment:**
        ```
        python run_pei_assessment.py \\
          --log logs/{st.session_state.current_run}.jsonl \\
          --evaluator llama3:latest \\
          --output logs/{st.session_state.current_run}_pei.json
        ```
        """)
