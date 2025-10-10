#!/usr/bin/env python3
"""ContReAct-Ollama Experiment Runner CLI.

This script initializes and executes ContReAct experiments based on YAML configuration files.

Usage:
    python scripts/run_experiment.py --config configs/sample-config.yaml

The script loads the specified configuration file, validates it, and prints the
parsed configuration to the console.
"""

# Standard library imports
import argparse
import sys
from pathlib import Path

# Third-party imports
import yaml

# Local application imports
from contreact_ollama.core.experiment_runner import ExperimentRunner


def main():
    """Main entry point for the experiment runner CLI."""
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Run ContReAct-Ollama experiments from configuration files'
    )
    parser.add_argument(
        '--config',
        type=str,
        required=True,
        help='Path to YAML configuration file (e.g., configs/sample-config.yaml)'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    try:
        # Create ExperimentRunner instance
        runner = ExperimentRunner(args.config)
        
        # Load configuration
        config = runner.load_config()
        
        # Print configuration to console
        print("\nSuccessfully loaded configuration:")
        print("-" * 50)
        print(f"Run ID: {config.run_id}")
        print(f"Model: {config.model_name}")
        print(f"Cycle Count: {config.cycle_count}")
        print(f"Ollama Host: {config.ollama_client_config.get('host', 'N/A')}")
        print("Model Options:")
        for key, value in config.model_options.items():
            print(f"  - {key}: {value}")
        print("-" * 50)
        print()
        
        # Initialize services (includes Ollama connection and model verification)
        print("Verifying Ollama connection and model availability...")
        services = runner.initialize_services()
        print(f"✓ Connected to Ollama server")
        print(f"✓ Model '{config.model_name}' is available")
        print()
        
        # Future: runner.run() will execute experiment
        
        # Exit with success code
        sys.exit(0)
        
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
        
    except (yaml.YAMLError, KeyError, TypeError, ValueError) as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
        
    except ConnectionError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    
    except Exception as e:
        # Catch ModelNotFoundError and other exceptions
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
