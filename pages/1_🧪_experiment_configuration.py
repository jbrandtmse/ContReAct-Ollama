"""
Experiment Configuration Page

This page provides a form interface for configuring ContReAct-Ollama experiments.
Users can define all experiment parameters including model options, cycle count, and Ollama settings.

Part of: Story 2.2 - Implement Experiment Configuration Form
Part of: Story 2.3 - Implement Configuration File Saving
"""
import streamlit as st
import yaml
from pathlib import Path
import re

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


def sanitize_filename(run_id: str) -> str:
    """
    Sanitize run_id for use as filename.
    
    Args:
        run_id: Run identifier from form
        
    Returns:
        Sanitized filename safe for all filesystems
        
    Example:
        >>> sanitize_filename("My Run #1")
        'My-Run-1'
    """
    # Replace spaces with hyphens
    filename = run_id.replace(' ', '-')
    
    # Remove invalid filesystem characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    
    # Remove any other non-alphanumeric except hyphens and underscores
    filename = re.sub(r'[^a-zA-Z0-9_-]', '', filename)
    
    # Remove leading/trailing hyphens and underscores
    filename = filename.strip('-_')
    
    # Ensure not empty
    if not filename:
        filename = "config"
    
    return filename


def save_config_to_yaml(config_data: dict, run_id: str) -> tuple[bool, str]:
    """
    Save configuration dictionary to YAML file.
    
    Args:
        config_data: Configuration dictionary
        run_id: Run identifier for filename
        
    Returns:
        Tuple of (success: bool, message: str)
        
    Creates configs/ directory if it doesn't exist.
    Saves file as configs/{sanitized_run_id}.yaml
    """
    try:
        # Ensure configs directory exists
        configs_dir = Path("configs")
        configs_dir.mkdir(exist_ok=True)
        
        # Sanitize filename
        filename = sanitize_filename(run_id)
        
        # Add .yaml extension if not present
        if not filename.endswith('.yaml'):
            filename += '.yaml'
        
        # Full file path
        file_path = configs_dir / filename
        
        # Write YAML file
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(
                config_data,
                f,
                default_flow_style=False,  # Use block style (more readable)
                sort_keys=False,            # Preserve key order
                allow_unicode=True,
                indent=2
            )
        
        return True, str(file_path)
        
    except PermissionError:
        return False, "Permission denied: Cannot write to configs/ directory. Check file permissions."
    except OSError as e:
        if "No space left on device" in str(e):
            return False, "Disk full: Not enough space to save configuration file."
        else:
            return False, f"File system error: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error saving configuration: {str(e)}"

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
            max_value=131072,
            value=DEFAULT_NUM_CTX,
            step=512,
            help="Context window size for the model (up to 128k)"
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
            
            # Save to YAML file
            success, message = save_config_to_yaml(config_data, run_id.strip())
            
            if success:
                st.success("✅ Configuration saved successfully!")
                st.info(f"� File saved to: `{message}`")
                
                # Provide next steps
                st.markdown(f"""
                ### Next Steps
                
                To run this experiment, use the following command:
                ```bash
                python scripts/run_experiment.py --config {message}
                ```
                """)
                
                # Preview configuration
                with st.expander("Preview Saved Configuration"):
                    st.json(config_data)
            else:
                st.error(f"❌ Failed to save configuration: {message}")

st.divider()
st.caption("💡 Tip: Configuration files are saved in the `configs/` directory")
