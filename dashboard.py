"""
ContReAct-Ollama Dashboard - Main Entry Point

This module provides the main landing page for the ContReAct-Ollama Experimental Platform.
It serves as the entry point for the Streamlit multi-page application and provides
navigation to experiment configuration and results analysis pages.

Usage:
    streamlit run dashboard.py
"""
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="ContReAct Ollama Platform",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main page content
st.title("🤖 ContReAct-Ollama Experimental Platform")

st.markdown("""
Welcome to the ContReAct-Ollama Experimental Platform! This platform enables you to:

- **Configure Experiments**: Define parameters for task-free agent exploration
- **View Results**: Analyze experiment logs, metrics, and agent behavior
- **Assess PEI**: Evaluate phenomenological experience across models

## Getting Started

Use the sidebar to navigate between pages:
- **🧪 Experiment Configuration**: Create and edit experiment configs
- **📊 Results Dashboard**: View and analyze completed experiments

## Quick Actions

1. **Create a New Experiment**: Go to Experiment Configuration
2. **View Results**: Go to Results Dashboard and select a completed run
3. **Run an Experiment**: Use the CLI: `python scripts/run_experiment.py --config configs/your-config.yaml`
""")

st.divider()

st.info("""
💡 **Tip**: Experiments are run via the command line. The dashboard is for configuration and analysis only.
""")
