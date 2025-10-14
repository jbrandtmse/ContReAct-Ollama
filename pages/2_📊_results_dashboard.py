"""
Results Dashboard Page

This page allows users to select and analyze completed experiment runs.
Provides run selection, data loading, and displays summary information.

Part of: Story 2.5 - Results Dashboard Run Selector and Data Loading
Part of: Story 2.6 - Display Summary Metrics on Dashboard
Part of: Story 2.7 - Display Raw Conversation Log on Dashboard
Part of: Story 2.8 - Implement Interactive Charts on Dashboard
"""
import json
import pandas as pd
from pathlib import Path
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from contreact_ollama.ui_utils import (
    get_log_files,
    load_log_file,
    extract_metrics_from_dataframe,
    calculate_summary_metrics,
    load_pei_assessment
)


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
    
    # Extract metrics using utility function
    metrics_df = extract_metrics_from_dataframe(df)
    
    if metrics_df is not None:
        # Calculate summary totals using utility function
        totals = calculate_summary_metrics(metrics_df)
        
        # Display key metrics with st.metric
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Memory Operations",
                value=totals['total_memory_ops']
            )
        
        with col2:
            st.metric(
                label="Messages to Operator",
                value=totals['total_messages']
            )
        
        with col3:
            st.metric(
                label="Response Characters",
                value=f"{totals['total_response_chars']:,}"
            )
        
        with col4:
            st.metric(
                label="Memory Write Characters",
                value=f"{totals['total_memory_chars']:,}"
            )
        
        st.divider()
        
        # Display full metrics table
        st.subheader("📊 Detailed Metrics by Cycle")
        
        # Reorder columns for better display
        display_columns = ['cycle_number', 'memory_ops_total', 'messages_to_operator', 
                         'response_chars', 'memory_write_chars']
        display_df = metrics_df[display_columns].copy()
        
        # Rename for clarity
        display_df.columns = ['Cycle', 'Memory Ops', 'Messages', 
                              'Response Chars', 'Memory Chars']
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("No metrics found in CYCLE_END events")
    
    st.divider()
    
    # Check for PEI assessment using utility function
    st.subheader("🧠 PEI Assessment Results")
    
    pei_data = load_pei_assessment(st.session_state.current_run)
    
    if pei_data is not None:
        st.success("✅ PEI Assessment found")
        
        # Display PEI results
        if isinstance(pei_data, dict):
            pei_df = pd.DataFrame([pei_data])
            st.dataframe(pei_df, use_container_width=True)
        elif isinstance(pei_data, list):
            pei_df = pd.DataFrame(pei_data)
            st.dataframe(pei_df, use_container_width=True)
        else:
            st.json(pei_data)
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
    
    st.divider()
    
    # Display conversation log
    with st.expander("💬 Raw Conversation Log", expanded=False):
        st.markdown("### Full Conversation History")
        st.caption("Complete message history and tool interactions from the experimental run")
        
        # Event type filter
        st.markdown("**Filter Event Types:**")
        all_event_types = ['CYCLE_START', 'LLM_INVOCATION', 'TOOL_CALL', 'CYCLE_END']
        selected_types = st.multiselect(
            "Select event types to display",
            options=all_event_types,
            default=all_event_types,
            key="event_type_filter"
        )
        
        # Filter DataFrame
        if selected_types:
            filtered_df = df[df['event_type'].isin(selected_types)].copy()
            st.caption(f"📊 Showing {len(filtered_df)} of {len(df)} events")
        else:
            filtered_df = pd.DataFrame()
            st.warning("⚠️ Select at least one event type to display")
        
        st.markdown("---")
        
        # Process filtered events chronologically
        for idx, row in filtered_df.iterrows():
            try:
                cycle = row.get('cycle_number', 'N/A')
                event_type = row.get('event_type', 'UNKNOWN')
                payload = row.get('payload', {})
                timestamp = row.get('timestamp', '')
                
                # Ensure payload is a dictionary
                if not isinstance(payload, dict):
                    continue
                
                if event_type == 'CYCLE_START':
                    st.markdown(f"---")
                    st.markdown(f"### 🔄 **Cycle {cycle} Start**")
                    st.caption(f"⏰ {timestamp}")
                
                elif event_type == 'LLM_INVOCATION':
                    st.markdown(f"#### 🤖 LLM Invocation (Cycle {cycle})")
                    
                    # Display prompt messages
                    if 'prompt_messages' in payload:
                        st.markdown("**Prompt Messages:**")
                        prompt_messages = payload['prompt_messages']
                        if isinstance(prompt_messages, list):
                            for msg in prompt_messages:
                                if isinstance(msg, dict):
                                    role = msg.get('role', 'unknown')
                                    content = msg.get('content', '')
                                    
                                    if role == 'system':
                                        st.info(f"**[SYSTEM]**\n\n{content}")
                                    elif role == 'user':
                                        st.success(f"**[USER]**\n\n{content}")
                                    elif role == 'assistant':
                                        st.warning(f"**[ASSISTANT]**\n\n{content}")
                                    elif role == 'tool':
                                        st.error(f"**[TOOL]**\n\n{content}")
                    
                    # Display response
                    if 'response_message' in payload:
                        st.markdown("**Response:**")
                        response = payload['response_message']
                        if isinstance(response, dict):
                            role = response.get('role', 'assistant')
                            content = response.get('content', '')
                            st.warning(f"**[{role.upper()}]**\n\n{content}")
                
                elif event_type == 'TOOL_CALL':
                    st.markdown(f"#### 🔧 Tool Call (Cycle {cycle})")
                    
                    tool_name = payload.get('tool_name', 'unknown')
                    parameters = payload.get('parameters', {})
                    output = payload.get('output', '')
                    
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.markdown(f"**Tool:** `{tool_name}`")
                        if isinstance(parameters, dict):
                            st.json(parameters)
                        else:
                            st.code(str(parameters))
                    
                    with col2:
                        st.markdown(f"**Output:**")
                        st.code(str(output), language=None)
                
                elif event_type == 'CYCLE_END':
                    st.markdown(f"#### 💭 Final Reflection (Cycle {cycle})")
                    
                    if 'final_reflection' in payload:
                        reflection = payload['final_reflection']
                        st.info(f"**Reflection:**\n\n{reflection}")
                    
                    if 'metrics' in payload:
                        metrics = payload['metrics']
                        if isinstance(metrics, dict):
                            st.caption(f"📊 Memory Ops: {metrics.get('memory_ops_total', 0)} | "
                                     f"Messages: {metrics.get('messages_to_operator', 0)} | "
                                     f"Response Chars: {metrics.get('response_chars', 0)}")
            
            except Exception as e:
                # Log error but continue processing other events
                st.warning(f"⚠️ Error processing event at index {idx}: {str(e)}")
                continue
        
        st.markdown("---")
        st.success("✅ End of conversation log")
    
    st.divider()
    
    # Interactive Charts Section
    st.subheader("📊 Interactive Charts")
    st.caption("Explore experimental data through interactive visualizations")
    
    try:
        # Prepare data for charts
        # Count tool calls per cycle
        tool_calls_df = df[df['event_type'] == 'TOOL_CALL'].groupby('cycle_number').size().reset_index(name='tool_calls')
        
        # Extract metrics from CYCLE_END events
        cycle_ends = df[df['event_type'] == 'CYCLE_END'].copy()
        
        if len(cycle_ends) > 0:
            metrics_data = []
            for idx, row in cycle_ends.iterrows():
                if 'payload' in row and isinstance(row['payload'], dict):
                    payload = row['payload']
                    if 'metrics' in payload:
                        metrics = payload['metrics']
                        metrics_data.append({
                            'cycle': row['cycle_number'],
                            'memory_ops': metrics.get('memory_ops_total', 0),
                            'messages': metrics.get('messages_to_operator', 0),
                            'response_chars': metrics.get('response_chars', 0),
                            'memory_chars': metrics.get('memory_write_chars', 0)
                        })
            
            if metrics_data:
                metrics_df = pd.DataFrame(metrics_data)
                
                # Chart 1: Tool Calls per Cycle (Bar Chart)
                st.markdown("#### 🔧 Tool Calls per Cycle")
                
                if len(tool_calls_df) > 0:
                    fig_tools = px.bar(
                        tool_calls_df,
                        x='cycle_number',
                        y='tool_calls',
                        title='Tool Calls by Cycle',
                        labels={'cycle_number': 'Cycle', 'tool_calls': 'Number of Tool Calls'},
                        color='tool_calls',
                        color_continuous_scale='Blues'
                    )
                    
                    fig_tools.update_layout(
                        hovermode='x unified',
                        xaxis=dict(tickmode='linear', tick0=1, dtick=1)
                    )
                    
                    st.plotly_chart(fig_tools, use_container_width=True)
                else:
                    st.info("No tool calls found in this run")
                
                # Chart 2: Response Length Over Time (Line Chart)
                st.markdown("#### 📝 Response Length Trend")
                
                fig_response = px.line(
                    metrics_df,
                    x='cycle',
                    y='response_chars',
                    title='Response Character Count Over Time',
                    labels={'cycle': 'Cycle', 'response_chars': 'Characters'},
                    markers=True
                )
                
                fig_response.update_layout(
                    hovermode='x unified',
                    xaxis=dict(tickmode='linear', tick0=1, dtick=1)
                )
                
                st.plotly_chart(fig_response, use_container_width=True)
                
                # Chart 3: Memory Operations (Bar Chart)
                st.markdown("#### 💾 Memory Operations by Cycle")
                
                fig_memory = px.bar(
                    metrics_df,
                    x='cycle',
                    y='memory_ops',
                    title='Memory Operations per Cycle',
                    labels={'cycle': 'Cycle', 'memory_ops': 'Memory Operations'},
                    color='memory_ops',
                    color_continuous_scale='Greens'
                )
                
                fig_memory.update_layout(
                    hovermode='x unified',
                    xaxis=dict(tickmode='linear', tick0=1, dtick=1)
                )
                
                st.plotly_chart(fig_memory, use_container_width=True)
                
                # Chart 4: Multi-metric Comparison (Grouped Bar)
                st.markdown("#### 📊 Metrics Comparison")
                
                # Melt dataframe for grouped bar chart
                melted_df = metrics_df.melt(
                    id_vars=['cycle'],
                    value_vars=['memory_ops', 'messages'],
                    var_name='Metric',
                    value_name='Count'
                )
                
                # Rename for display
                melted_df['Metric'] = melted_df['Metric'].map({
                    'memory_ops': 'Memory Operations',
                    'messages': 'Messages to Operator'
                })
                
                fig_compare = px.bar(
                    melted_df,
                    x='cycle',
                    y='Count',
                    color='Metric',
                    barmode='group',
                    title='Memory Operations vs Messages by Cycle',
                    labels={'cycle': 'Cycle', 'Count': 'Count'}
                )
                
                fig_compare.update_layout(
                    hovermode='x unified',
                    xaxis=dict(tickmode='linear', tick0=1, dtick=1)
                )
                
                st.plotly_chart(fig_compare, use_container_width=True)
            else:
                st.warning("No metrics data available for charts")
        else:
            st.warning("No CYCLE_END events found for chart generation")
    
    except Exception as e:
        st.error(f"Error generating charts: {e}")
        st.info("Charts could not be rendered. Please check the log file format.")
