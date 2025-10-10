# Standard library imports
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class ExperimentConfig:
    """Configuration for a single experimental run.
    
    This dataclass encapsulates all parameters needed to execute a ContReAct
    experiment, including model selection, cycle count, Ollama client settings,
    and LLM generation parameters.
    
    Attributes:
        run_id: Unique identifier for this specific experimental run
        model_name: Model tag as recognized by local Ollama server (e.g., 'llama3:latest')
        cycle_count: Total number of operational cycles to execute
        ollama_client_config: Configuration dict for Ollama client (e.g., {'host': 'http://localhost:11434'})
        model_options: Parameters for LLM generation (temperature, seed, top_p, etc.)
    """
    
    run_id: str
    model_name: str
    cycle_count: int
    ollama_client_config: Dict[str, Any]
    model_options: Dict[str, Any]
