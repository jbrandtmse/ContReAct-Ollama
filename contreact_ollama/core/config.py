# Standard library imports
import os
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


class InvalidConfigurationError(Exception):
    """Raised when configuration file is invalid or missing required fields."""
    pass


@dataclass
class ExperimentConfig:
    """Configuration for a single experimental run.
    
    This dataclass encapsulates all parameters needed to execute a ContReAct
    experiment, including model selection, cycle count, Ollama client settings,
    LLM generation parameters, and optional Telegram integration.
    
    Attributes:
        run_id: Unique identifier for this specific experimental run
        model_name: Model tag as recognized by local Ollama server (e.g., 'llama3:latest')
        cycle_count: Total number of operational cycles to execute
        ollama_client_config: Configuration dict for Ollama client (e.g., {'host': 'http://localhost:11434'})
        model_options: Parameters for LLM generation (temperature, seed, top_p, etc.)
        telegram_enabled: Whether to enable Telegram operator communication (default: False)
        telegram_bot_token: Bot token from environment variable (sourced from TELEGRAM_BOT_TOKEN)
        telegram_authorized_users: List of authorized Telegram user IDs
        telegram_timeout_minutes: Response timeout in minutes (-1 = wait forever, 0-120 = timeout)
    """
    
    run_id: str
    model_name: str
    cycle_count: int
    ollama_client_config: Dict[str, Any]
    model_options: Dict[str, Any]
    telegram_enabled: bool = False
    telegram_bot_token: Optional[str] = None
    telegram_authorized_users: List[int] = field(default_factory=list)
    telegram_timeout_minutes: int = 5
    
    def validate_telegram_config(self) -> None:
        """Validate Telegram configuration fields.
        
        Raises:
            InvalidConfigurationError: If Telegram is enabled but configuration is invalid
            
        Validates:
            - Bot token environment variable is set when Telegram is enabled
            - At least one authorized user is configured
            - Timeout is within valid range (-1 or 0-120 minutes)
        """
        if self.telegram_enabled:
            # Check if bot token environment variable is set
            bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
            if not bot_token:
                raise InvalidConfigurationError(
                    "Telegram enabled but TELEGRAM_BOT_TOKEN environment variable not set. "
                    "See README.md 'Telegram Integration Setup' section for configuration instructions."
                )
            
            # Check if authorized users are configured
            if not self.telegram_authorized_users:
                raise InvalidConfigurationError(
                    "Telegram enabled but no authorized users configured. "
                    "Add at least one user ID to telegram_authorized_users list."
                )
            
            # Validate timeout range
            if self.telegram_timeout_minutes < -1 or self.telegram_timeout_minutes > 120:
                raise InvalidConfigurationError(
                    f"telegram_timeout_minutes must be -1 (wait forever) or between 0 and 120, "
                    f"got {self.telegram_timeout_minutes}"
                )
