# Standard library imports
from pathlib import Path
from typing import Dict, Any

# Third-party imports
import yaml

# Local application imports
from contreact_ollama.core.config import ExperimentConfig


class ExperimentRunner:
    """Orchestrates the execution of ContReAct experiments.
    
    This class handles loading experiment configurations from YAML files,
    initializing required services, and executing the full experimental run.
    
    Attributes:
        config_path: Path to the YAML configuration file
    """
    
    def __init__(self, config_path: str):
        """Initialize runner with path to configuration file.
        
        Args:
            config_path: Path to YAML configuration file
        """
        self.config_path = config_path
    
    def load_config(self) -> ExperimentConfig:
        """Load and validate YAML configuration file.
        
        Returns:
            ExperimentConfig: Parsed and validated configuration object
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If YAML syntax is invalid
            KeyError: If required field is missing
            TypeError: If field value has incorrect type
            ValueError: If field value is invalid (e.g., cycle_count <= 0)
            
        Example:
            >>> runner = ExperimentRunner("configs/sample-config.yaml")
            >>> config = runner.load_config()
            >>> print(config.run_id)
            'llama3-experiment-001'
        """
        # Validate file existence
        config_file = Path(self.config_path)
        if not config_file.exists():
            raise FileNotFoundError(
                f"Error: Configuration file not found: {self.config_path}\n"
                f"Please check the file path and try again."
            )
        
        # Parse YAML file
        try:
            with open(config_file, 'r') as f:
                config_dict = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise yaml.YAMLError(
                f"Error: Invalid YAML syntax in configuration file: {e}\n"
                f"Please validate your YAML syntax and try again."
            )
        
        # Validate required fields
        required_fields = ['run_id', 'model_name', 'cycle_count', 'ollama_client_config', 'model_options']
        for field in required_fields:
            if field not in config_dict:
                raise KeyError(
                    f"Error: Missing required field in configuration: {field}\n"
                    f"Required fields: {', '.join(required_fields)}"
                )
        
        # Validate field types
        if not isinstance(config_dict['run_id'], str):
            raise TypeError(
                f"Error: Invalid value for field 'run_id': must be a string\n"
                f"Please check the sample configuration for expected value types."
            )
        
        if not isinstance(config_dict['model_name'], str):
            raise TypeError(
                f"Error: Invalid value for field 'model_name': must be a string\n"
                f"Please check the sample configuration for expected value types."
            )
        
        if not isinstance(config_dict['cycle_count'], int):
            raise TypeError(
                f"Error: Invalid value for field 'cycle_count': must be an integer\n"
                f"Please check the sample configuration for expected value types."
            )
        
        if config_dict['cycle_count'] <= 0:
            raise ValueError(
                f"Error: Invalid value for field 'cycle_count': must be greater than 0\n"
                f"Please check the sample configuration for expected value types."
            )
        
        if not isinstance(config_dict['ollama_client_config'], dict):
            raise TypeError(
                f"Error: Invalid value for field 'ollama_client_config': must be a dictionary\n"
                f"Please check the sample configuration for expected value types."
            )
        
        if not isinstance(config_dict['model_options'], dict):
            raise TypeError(
                f"Error: Invalid value for field 'model_options': must be a dictionary\n"
                f"Please check the sample configuration for expected value types."
            )
        
        # Create and return ExperimentConfig
        return ExperimentConfig(**config_dict)
