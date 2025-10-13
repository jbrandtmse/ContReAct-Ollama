"""
Experiment Configuration Page

This page provides a form interface for configuring ContReAct-Ollama experiments.
Users can define all experiment parameters including model options, cycle count, and Ollama settings.

Part of: Story 2.2 - Implement Experiment Configuration Form
"""
import streamlit as st

# Configuration defaults
DEFAULT_MODEL = "llama3:latest"
DEFAULT_CYCLE_COUNT = 10
DEFAULT_OLLAMA_HOST = "http://192.168.0.123:11434"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TOP_P = 0.9
DEFAULT_NUM_PREDICT = 2048
DEFAULT_SEED = 42
DEFAULT_REPEAT_LAST_N = 64
DEFAULT_REPEAT_PENALTY = 1.1
DEFAULT_NUM_CTX = 4096

# Validation constants
MIN_TEMPERATURE = 0.0
MAX_TEMPERATURE = 2.0
MIN_TOP_P = 0.0
MAX_TOP_P = 1.0

st.title("🧪 Experiment Configuration")

st.write("""
Configure your ContReAct-Ollama experiment parameters below. 
All fields marked with * are required.
""")

# Form for configuration
with st.form("config_form"):
    st.subheader("Basic Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        run_id = st.text_input(
            "Run ID *",
            value="",
            help="Unique identifier for this experiment run (e.g., 'llama3-exploration-001')",
            placeholder="my-experiment-001"
        )
    
    with col2:
        model_name = st.text_input(
            "Model Name *",
            value=DEFAULT_MODEL,
            help="Ollama model tag (e.g., 'llama3:latest', 'mistral:7b')"
        )
    
    cycle_count = st.number_input(
        "Cycle Count *",
        min_value=1,
        max_value=100,
        value=DEFAULT_CYCLE_COUNT,
        step=1,
        help="Number of exploration cycles to run"
    )
    
    st.divider()
    st.subheader("Ollama Client Configuration")
    
    ollama_host = st.text_input(
        "Ollama Host",
        value=DEFAULT_OLLAMA_HOST,
        help="URL of the Ollama server"
    )
    
    st.divider()
    st.subheader("Model Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        temperature = st.number_input(
            "Temperature",
            min_value=MIN_TEMPERATURE,
            max_value=MAX_TEMPERATURE,
            value=DEFAULT_TEMPERATURE,
            step=0.1,
            help="Controls randomness (0.0 = deterministic, 2.0 = very random)"
        )
        
        num_predict = st.number_input(
            "Max Tokens",
            min_value=-1,
            max_value=100000,
            value=DEFAULT_NUM_PREDICT,
            step=256,
            help="Maximum tokens to generate (-1 = unlimited)"
        )
    
    with col2:
        top_p = st.number_input(
            "Top P",
            min_value=MIN_TOP_P,
            max_value=MAX_TOP_P,
            value=DEFAULT_TOP_P,
            step=0.05,
            help="Nucleus sampling threshold"
        )
        
        use_seed = st.checkbox("Set Random Seed", value=False)
        seed = st.number_input(
            "Seed",
            min_value=0,
            max_value=999999,
            value=DEFAULT_SEED,
            disabled=not use_seed,
            help="Random seed for reproducibility"
        )
    
    # Advanced options in expander
    with st.expander("Advanced Model Options"):
        repeat_last_n = st.number_input(
            "Repeat Last N",
            min_value=-1,
            max_value=256,
            value=DEFAULT_REPEAT_LAST_N,
            help="How far back model looks to prevent repetition"
        )
        
        repeat_penalty = st.number_input(
            "Repeat Penalty",
            min_value=0.0,
            max_value=2.0,
            value=DEFAULT_REPEAT_PENALTY,
            step=0.1,
            help="How strongly to penalize repetitions"
        )
        
        num_ctx = st.number_input(
            "Context Window Size",
            min_value=512,
            max_value=32768,
            value=DEFAULT_NUM_CTX,
            step=512,
            help="Context window size for the model"
        )
    
    st.divider()
    
    # Submit button
    submitted = st.form_submit_button(
        "Save Configuration",
        type="primary",
        use_container_width=True
    )
    
    # Form validation and processing
    if submitted:
        # Validation (note: number_input widgets already enforce min/max constraints)
        errors = []
        
        if not run_id or run_id.strip() == "":
            errors.append("Run ID cannot be empty")
        
        if errors:
            for error in errors:
                st.error(f"❌ {error}")
        else:
            # Build configuration dict (will be used in Story 2.3)
            config_data = {
                "run_id": run_id.strip(),
                "model_name": model_name.strip(),
                "cycle_count": cycle_count,
                "ollama_client_config": {
                    "host": ollama_host.strip()
                },
                "model_options": {
                    "temperature": temperature,
                    "top_p": top_p,
                    "num_predict": num_predict
                }
            }
            
            # Add optional seed if checkbox is checked
            if use_seed:
                config_data["model_options"]["seed"] = seed
            
            # Add advanced options if different from defaults
            if repeat_last_n != DEFAULT_REPEAT_LAST_N:
                config_data["model_options"]["repeat_last_n"] = repeat_last_n
            if repeat_penalty != DEFAULT_REPEAT_PENALTY:
                config_data["model_options"]["repeat_penalty"] = repeat_penalty
            if num_ctx != DEFAULT_NUM_CTX:
                config_data["model_options"]["num_ctx"] = num_ctx
            
            st.success("✅ Configuration validated successfully!")
            st.info("💾 File saving will be implemented in Story 2.3")
            
            # Preview configuration
            with st.expander("Preview Configuration"):
                st.json(config_data)

st.divider()
st.caption("💡 Tip: Required fields are marked with *")
