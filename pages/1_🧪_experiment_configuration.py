"""
Experiment Configuration Page

This page provides a form interface for configuring ContReAct-Ollama experiments.
Users can define all experiment parameters including model options, cycle count, and Ollama settings.

Part of: Story 2.2 - Implement Experiment Configuration Form
Part of: Story 2.3 - Implement Configuration File Saving
Part of: Story 2.4 - Implement Configuration File Loading and Editing
Part of: Story 3.1 - Telegram Configuration (Backend & UI)
"""
import streamlit as st
import yaml
from pathlib import Path
import re
import os
from typing import Optional

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

# Directory constants
CONFIGS_DIR = "configs"


def get_config_files() -> list[str]:
    """
    Scan configs/ directory for YAML files.
    
    Returns:
        Sorted list of YAML filenames, empty list if directory doesn't exist
        
    Example:
        >>> get_config_files()
        ['experiment-001.yaml', 'test-config.yaml']
    """
    configs_dir = Path(CONFIGS_DIR)
    if not configs_dir.exists():
        return []
    
    yaml_files = list(configs_dir.glob("*.yaml"))
    return sorted([f.name for f in yaml_files])


def load_config_file(filename: str) -> Optional[dict]:
    """
    Load YAML config file from configs/ directory.
    
    Args:
        filename: Name of the YAML file to load
        
    Returns:
        Configuration dictionary or None if loading fails
        
    Example:
        >>> config = load_config_file('my-experiment.yaml')
        >>> config['run_id']
        'my-experiment'
    """
    try:
        file_path = Path(CONFIGS_DIR) / filename
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        st.error(f"Error parsing YAML file: {e}")
        return None
    except FileNotFoundError:
        st.error(f"Configuration file not found: {filename}")
        return None
    except Exception as e:
        st.error(f"Error loading config: {e}")
        return None


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
        configs_dir = Path(CONFIGS_DIR)
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
        return False, f"Permission denied: Cannot write to {CONFIGS_DIR}/ directory. Check file permissions."
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

# Config file selector section
st.subheader("Load Existing Configuration")
config_files = get_config_files()

# Initialize session state for loaded config tracking
if 'loaded_config' not in st.session_state:
    st.session_state.loaded_config = None
if 'current_file' not in st.session_state:
    st.session_state.current_file = None

if config_files:
    selected_option = st.selectbox(
        "Select Configuration",
        options=["Create New Configuration"] + config_files,
        index=0,
        help="Choose an existing configuration to edit or create a new one"
    )
    
    # Handle config loading
    if selected_option != "Create New Configuration":
        # Load config if different from currently loaded
        if st.session_state.current_file != selected_option:
            loaded_config = load_config_file(selected_option)
            if loaded_config:
                st.session_state.loaded_config = loaded_config
                st.session_state.current_file = selected_option
                st.rerun()
        
        # Display loaded config info
        if st.session_state.loaded_config:
            st.info(f"📂 Loaded: `{selected_option}`")
    else:
        # Clear loaded config when creating new
        if st.session_state.loaded_config is not None:
            st.session_state.loaded_config = None
            st.session_state.current_file = None
            st.rerun()
else:
    st.info("No saved configurations found. Create a new one below.")

st.divider()

# Get values from loaded config or use defaults
if st.session_state.loaded_config:
    config = st.session_state.loaded_config
    default_run_id = config.get('run_id', '')
    default_model = config.get('model_name', DEFAULT_MODEL)
    default_cycles = config.get('cycle_count', DEFAULT_CYCLE_COUNT)
    default_host = config.get('ollama_client_config', {}).get('host', DEFAULT_OLLAMA_HOST)
    model_opts = config.get('model_options', {})
    default_temp = model_opts.get('temperature', DEFAULT_TEMPERATURE)
    default_top_p = model_opts.get('top_p', DEFAULT_TOP_P)
    default_num_predict = model_opts.get('num_predict', DEFAULT_NUM_PREDICT)
    default_seed_value = model_opts.get('seed', DEFAULT_SEED)
    has_seed = 'seed' in model_opts
    default_repeat_last_n = model_opts.get('repeat_last_n', DEFAULT_REPEAT_LAST_N)
    default_repeat_penalty = model_opts.get('repeat_penalty', DEFAULT_REPEAT_PENALTY)
    default_num_ctx = model_opts.get('num_ctx', DEFAULT_NUM_CTX)
    # Telegram configuration
    default_telegram_enabled = config.get('telegram_enabled', False)
    default_telegram_users = ','.join(str(uid) for uid in config.get('telegram_authorized_users', []))
    default_telegram_timeout = config.get('telegram_timeout_minutes', 5)
else:
    default_run_id = ''
    default_model = DEFAULT_MODEL
    default_cycles = DEFAULT_CYCLE_COUNT
    default_host = DEFAULT_OLLAMA_HOST
    default_temp = DEFAULT_TEMPERATURE
    default_top_p = DEFAULT_TOP_P
    default_num_predict = DEFAULT_NUM_PREDICT
    default_seed_value = DEFAULT_SEED
    has_seed = False
    default_repeat_last_n = DEFAULT_REPEAT_LAST_N
    default_repeat_penalty = DEFAULT_REPEAT_PENALTY
    default_num_ctx = DEFAULT_NUM_CTX
    # Telegram configuration
    default_telegram_enabled = False
    default_telegram_users = ''
    default_telegram_timeout = 5

# Form for configuration
with st.form("config_form"):
    st.subheader("Basic Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        run_id = st.text_input(
            "Run ID *",
            value=default_run_id,
            help="Unique identifier for this experiment run (e.g., 'llama3-exploration-001')",
            placeholder="my-experiment-001"
        )
    
    with col2:
        model_name = st.text_input(
            "Model Name *",
            value=default_model,
            help="Ollama model tag (e.g., 'llama3:latest', 'mistral:7b')"
        )
    
    cycle_count = st.number_input(
        "Cycle Count *",
        min_value=1,
        max_value=100,
        value=default_cycles,
        step=1,
        help="Number of exploration cycles to run"
    )
    
    st.divider()
    st.subheader("Ollama Client Configuration")
    
    ollama_host = st.text_input(
        "Ollama Host",
        value=default_host,
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
            value=default_temp,
            step=0.1,
            help="Controls randomness (0.0 = deterministic, 2.0 = very random)"
        )
        
        num_predict = st.number_input(
            "Max Tokens",
            min_value=-1,
            max_value=100000,
            value=default_num_predict,
            step=256,
            help="Maximum tokens to generate (-1 = unlimited)"
        )
    
    with col2:
        top_p = st.number_input(
            "Top P",
            min_value=MIN_TOP_P,
            max_value=MAX_TOP_P,
            value=default_top_p,
            step=0.05,
            help="Nucleus sampling threshold"
        )
        
        use_seed = st.checkbox("Set Random Seed", value=has_seed)
        seed = st.number_input(
            "Seed",
            min_value=0,
            max_value=999999,
            value=default_seed_value,
            disabled=not use_seed,
            help="Random seed for reproducibility"
        )
    
    # Advanced options in expander
    with st.expander("Advanced Model Options"):
        repeat_last_n = st.number_input(
            "Repeat Last N",
            min_value=-1,
            max_value=256,
            value=default_repeat_last_n,
            help="How far back model looks to prevent repetition"
        )
        
        repeat_penalty = st.number_input(
            "Repeat Penalty",
            min_value=0.0,
            max_value=2.0,
            value=default_repeat_penalty,
            step=0.1,
            help="How strongly to penalize repetitions"
        )
        
        num_ctx = st.number_input(
            "Context Window Size",
            min_value=512,
            max_value=131072,
            value=default_num_ctx,
            step=512,
            help="Context window size for the model (up to 128k)"
        )
    
    st.divider()
    st.subheader("Telegram Integration")
    
    telegram_enabled = st.checkbox(
        "Enable Telegram Operator Communication",
        value=default_telegram_enabled,
        help="Enable remote operator communication via Telegram bot during experiments"
    )
    
    # Check environment variable status
    bot_token_set = os.getenv('TELEGRAM_BOT_TOKEN') is not None
    st.text_input(
        "Bot Token Status",
        value="✓ Set" if bot_token_set else "✗ Not Set",
        disabled=True,
        help="Set TELEGRAM_BOT_TOKEN environment variable. See README for setup instructions."
    )
    
    telegram_users = st.text_input(
        "Authorized User IDs",
        value=default_telegram_users,
        placeholder="123456789, 987654321",
        disabled=not telegram_enabled,
        help="Comma-separated list of Telegram user IDs authorized to interact with the bot"
    )
    
    telegram_timeout = st.number_input(
        "Response Timeout (minutes)",
        min_value=-1,
        max_value=120,
        value=default_telegram_timeout,
        disabled=not telegram_enabled,
        help="Minutes to wait for operator response. -1 = wait forever (no timeout), 0-120 = timeout in minutes"
    )
    
    if telegram_enabled:
        st.info(
            "📚 **Setup Guide**: See the [Telegram Integration Setup](#telegram-integration-setup) "
            "section in README.md for detailed instructions on creating a bot and finding user IDs."
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
        
        # Telegram validation
        if telegram_enabled:
            if not bot_token_set:
                errors.append("Telegram enabled but TELEGRAM_BOT_TOKEN environment variable not set")
            if not telegram_users or telegram_users.strip() == "":
                errors.append("Telegram enabled but no authorized user IDs provided")
            else:
                # Validate user IDs format
                try:
                    user_id_list = [uid.strip() for uid in telegram_users.split(',')]
                    parsed_user_ids = [int(uid) for uid in user_id_list if uid]
                    if not parsed_user_ids:
                        errors.append("Telegram enabled but no valid user IDs provided")
                except ValueError:
                    errors.append("Invalid user ID format. User IDs must be numeric values separated by commas")
        
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
            
            # Add Telegram configuration
            config_data["telegram_enabled"] = telegram_enabled
            if telegram_enabled:
                # Parse user IDs from comma-separated string
                user_id_list = [uid.strip() for uid in telegram_users.split(',')]
                config_data["telegram_authorized_users"] = [int(uid) for uid in user_id_list if uid]
                config_data["telegram_timeout_minutes"] = telegram_timeout
            else:
                config_data["telegram_authorized_users"] = []
                config_data["telegram_timeout_minutes"] = 5
            
            # Determine if overwriting existing file
            is_overwrite = st.session_state.current_file is not None
            
            # Save to YAML file
            success, message = save_config_to_yaml(config_data, run_id.strip())
            
            if success:
                if is_overwrite:
                    st.success(f"✅ Configuration updated successfully!")
                    st.info(f"📁 File overwritten: `{message}`")
                else:
                    st.success("✅ Configuration saved successfully!")
                    st.info(f"📁 File saved to: `{message}`")
                
                # Update session state to reflect saved file
                saved_filename = Path(message).name
                st.session_state.current_file = saved_filename
                st.session_state.loaded_config = config_data
                
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
st.caption(f"💡 Tip: Configuration files are saved in the `{CONFIGS_DIR}/` directory")
