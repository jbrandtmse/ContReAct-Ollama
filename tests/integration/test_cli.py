# Standard library imports
import subprocess
import sys
from pathlib import Path

# Third-party imports
import pytest


class TestCLI:
    """Integration tests for run_experiment.py CLI script."""
    
    def test_cli_with_valid_config_exits_zero(self):
        """Test that CLI exits with code 0 for valid configuration."""
        # Run CLI with valid config
        result = subprocess.run(
            [sys.executable, 'scripts/run_experiment.py', '--config', 'tests/fixtures/sample_config.yaml'],
            capture_output=True,
            text=True
        )
        
        # Assert exit code 0
        assert result.returncode == 0
        
        # Assert config printed to stdout
        assert 'Successfully loaded configuration' in result.stdout
        assert 'test-integration-run' in result.stdout
        assert 'llama3:latest' in result.stdout
        assert 'Cycle Count: 5' in result.stdout
    
    def test_cli_with_invalid_file_exits_nonzero(self):
        """Test that CLI exits with non-zero code for non-existent file."""
        # Run CLI with non-existent file
        result = subprocess.run(
            [sys.executable, 'scripts/run_experiment.py', '--config', 'nonexistent.yaml'],
            capture_output=True,
            text=True
        )
        
        # Assert exit code 1
        assert result.returncode == 1
        
        # Assert error message in stderr
        assert 'Configuration file not found' in result.stderr
        assert 'nonexistent.yaml' in result.stderr
    
    def test_cli_with_malformed_yaml_exits_nonzero(self):
        """Test that CLI exits with non-zero code for malformed YAML."""
        # Run CLI with malformed YAML
        result = subprocess.run(
            [sys.executable, 'scripts/run_experiment.py', '--config', 'configs/test-malformed.yaml'],
            capture_output=True,
            text=True
        )
        
        # Assert exit code 1
        assert result.returncode == 1
        
        # Assert error message in stderr
        assert 'Error:' in result.stderr
    
    def test_cli_without_config_argument_fails(self):
        """Test that CLI fails when --config argument is not provided."""
        # Run CLI without --config argument
        result = subprocess.run(
            [sys.executable, 'scripts/run_experiment.py'],
            capture_output=True,
            text=True
        )
        
        # Assert exit code 2 (argparse error)
        assert result.returncode == 2
        
        # Assert usage/error message in stderr
        assert 'required' in result.stderr or 'usage' in result.stderr
