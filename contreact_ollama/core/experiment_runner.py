# Standard library imports
from pathlib import Path
from typing import Dict, Any

# Third-party imports
import yaml

# Local application imports
from contreact_ollama.core.config import ExperimentConfig
from contreact_ollama.core.cycle_orchestrator import CycleOrchestrator
from contreact_ollama.llm.ollama_interface import OllamaInterface
from contreact_ollama.logging.jsonl_logger import JsonlLogger
from contreact_ollama.tools.memory_tools import MemoryTools
from contreact_ollama.tools.tool_dispatcher import ToolDispatcher


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
    
    def initialize_services(self) -> Dict[str, Any]:
        """
        Initialize all required services (Ollama, Logger, Tools, etc.).
        
        Returns:
            Dictionary containing initialized service instances
            
        Raises:
            ConnectionError: If Ollama connection fails
            ModelNotFoundError: If model not available
            
        Example:
            >>> runner = ExperimentRunner("configs/sample-config.yaml")
            >>> config = runner.load_config()
            >>> services = runner.initialize_services()
            >>> print(services['ollama'])
            <OllamaInterface object>
        """
        # Load config if not already loaded
        config = self.load_config()
        
        services = {}
        
        # Initialize Ollama interface
        host = config.ollama_client_config.get('host', 'http://localhost:11434')
        ollama_interface = OllamaInterface(host=host)
        
        # Verify model availability
        ollama_interface.verify_model_availability(config.model_name)
        
        services['ollama'] = ollama_interface
        
        # Initialize logger
        log_file_path = f"logs/{config.run_id}.jsonl"
        logger = JsonlLogger(log_file_path)
        services['logger'] = logger
        
        # Initialize memory tools
        db_path = "data/memory.db"
        memory_tools = MemoryTools(db_path=db_path, run_id=config.run_id)
        services['memory_tools'] = memory_tools
        
        # Initialize tool dispatcher
        tool_dispatcher = ToolDispatcher(memory_tools=memory_tools)
        services['tool_dispatcher'] = tool_dispatcher
        
        # NOTE: SimilarityMonitor will be added in Story 1.10
        
        return services
    
    def run(self) -> None:
        """Execute the complete experimental run.
        
        Orchestrates the full experiment lifecycle:
        1. Load configuration
        2. Initialize services
        3. Create and run orchestrator
        4. Cleanup resources
        """
        # Load config if not already loaded
        if not hasattr(self, 'config'):
            self.config = self.load_config()
        
        # Initialize services if not already done
        if not hasattr(self, 'services'):
            self.services = self.initialize_services()
        
        try:
            # Create orchestrator with services
            orchestrator = CycleOrchestrator(
                config=self.config,
                ollama_interface=self.services['ollama'],
                tool_dispatcher=self.services['tool_dispatcher'],
                logger=self.services['logger']
            )
            
            # Run the experiment
            orchestrator.run_experiment()
        finally:
            # Clean up resources
            self.services['logger'].close()
            self.services['memory_tools'].close()
