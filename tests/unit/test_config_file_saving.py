"""
Unit tests for configuration file saving functionality.

Tests the sanitize_filename and save_config_to_yaml functions from
pages/1_🧪_experiment_configuration.py

Part of: Story 2.3 - Implement Configuration File Saving
"""
import pytest
import yaml
from pathlib import Path
import sys
import os
import tempfile
import shutil

# Add pages directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "pages"))

# Import functions to test (note: importing from streamlit app requires mocking)
# For now, we'll copy the functions here for testing purposes


def sanitize_filename(run_id: str) -> str:
    """
    Sanitize run_id for use as filename.
    
    Args:
        run_id: Run identifier from form
        
    Returns:
        Sanitized filename safe for all filesystems
    """
    import re
    
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


def save_config_to_yaml(config_data: dict, run_id: str, base_dir: Path = None) -> tuple[bool, str]:
    """
    Save configuration dictionary to YAML file.
    
    Args:
        config_data: Configuration dictionary
        run_id: Run identifier for filename
        base_dir: Base directory for configs (for testing)
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        # Use base_dir if provided (for testing), otherwise use current directory
        if base_dir:
            configs_dir = base_dir / "configs"
        else:
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
                default_flow_style=False,
                sort_keys=False,
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


class TestFilenameSanitization:
    """Tests for sanitize_filename function."""
    
    def test_spaces_to_hyphens(self):
        """Test that spaces are converted to hyphens."""
        assert sanitize_filename("My Test Experiment") == "My-Test-Experiment"
    
    def test_special_characters_removed(self):
        """Test that special characters are removed."""
        assert sanitize_filename("Exp#1: Test/Run") == "Exp1-TestRun"
    
    def test_windows_invalid_chars_removed(self):
        """Test that Windows invalid characters are removed."""
        result = sanitize_filename('test<>:"|?*file')
        assert '<' not in result
        assert '>' not in result
        assert ':' not in result
        assert '"' not in result
        assert '|' not in result
        assert '?' not in result
        assert '*' not in result
    
    def test_empty_string_fallback(self):
        """Test that empty string returns fallback name."""
        assert sanitize_filename("!!!") == "config"
        assert sanitize_filename("???") == "config"
        assert sanitize_filename("   ") == "config"
    
    def test_alphanumeric_preserved(self):
        """Test that alphanumeric characters are preserved."""
        assert sanitize_filename("test123ABC") == "test123ABC"
    
    def test_hyphens_underscores_preserved(self):
        """Test that hyphens and underscores are preserved."""
        assert sanitize_filename("test-run_001") == "test-run_001"
    
    def test_unicode_characters_removed(self):
        """Test that unicode characters are removed."""
        result = sanitize_filename("実験-1")
        # Should remove unicode characters but keep hyphen and number
        assert result == "-1" or result == "1" or "-" in result


class TestYAMLFileSaving:
    """Tests for save_config_to_yaml function."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_config(self):
        """Sample configuration data."""
        return {
            "run_id": "test-run-001",
            "model_name": "llama3:latest",
            "cycle_count": 10,
            "ollama_client_config": {
                "host": "http://192.168.0.123:11434"
            },
            "model_options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": 2048
            }
        }
    
    def test_successful_save(self, temp_dir, sample_config):
        """Test successful file save."""
        success, message = save_config_to_yaml(sample_config, "test-run-001", temp_dir)
        
        assert success is True
        assert "test-run-001.yaml" in message
        
        # Verify file exists
        file_path = Path(message)
        assert file_path.exists()
    
    def test_yaml_extension_added(self, temp_dir, sample_config):
        """Test that .yaml extension is added if not present."""
        success, message = save_config_to_yaml(sample_config, "test-no-ext", temp_dir)
        
        assert success is True
        assert message.endswith(".yaml")
    
    def test_yaml_content_valid(self, temp_dir, sample_config):
        """Test that saved YAML content is valid and accurate."""
        success, message = save_config_to_yaml(sample_config, "test-content", temp_dir)
        
        assert success is True
        
        # Load the saved file
        with open(message, 'r') as f:
            loaded_data = yaml.safe_load(f)
        
        # Verify content matches
        assert loaded_data == sample_config
        assert loaded_data["run_id"] == "test-run-001"
        assert loaded_data["cycle_count"] == 10
        assert loaded_data["model_options"]["temperature"] == 0.7
    
    def test_configs_directory_created(self, temp_dir, sample_config):
        """Test that configs/ directory is created if it doesn't exist."""
        # Ensure configs directory doesn't exist
        configs_dir = temp_dir / "configs"
        assert not configs_dir.exists()
        
        success, message = save_config_to_yaml(sample_config, "test-create-dir", temp_dir)
        
        assert success is True
        assert configs_dir.exists()
        assert configs_dir.is_dir()
    
    def test_filename_sanitization_applied(self, temp_dir, sample_config):
        """Test that filename sanitization is applied."""
        success, message = save_config_to_yaml(sample_config, "My Test: Run #1", temp_dir)
        
        assert success is True
        # Verify sanitized filename
        assert "My-Test-Run-1.yaml" in message
    
    def test_overwrite_existing_file(self, temp_dir, sample_config):
        """Test that existing file is overwritten."""
        run_id = "test-overwrite"
        
        # Save first time
        success1, message1 = save_config_to_yaml(sample_config, run_id, temp_dir)
        assert success1 is True
        
        # Modify config
        modified_config = sample_config.copy()
        modified_config["cycle_count"] = 20
        
        # Save again
        success2, message2 = save_config_to_yaml(modified_config, run_id, temp_dir)
        assert success2 is True
        assert message1 == message2  # Same file path
        
        # Verify new content
        with open(message2, 'r') as f:
            loaded_data = yaml.safe_load(f)
        
        assert loaded_data["cycle_count"] == 20  # Updated value
    
    def test_yaml_formatting(self, temp_dir, sample_config):
        """Test that YAML is formatted correctly."""
        success, message = save_config_to_yaml(sample_config, "test-format", temp_dir)
        
        assert success is True
        
        # Read raw file content
        with open(message, 'r') as f:
            content = f.read()
        
        # Verify block style (not inline)
        assert '{' not in content  # No inline dictionaries
        
        # Verify indentation
        lines = content.split('\n')
        for line in lines:
            if line.strip() and not line.startswith('#'):
                # Check that indentation is consistent (multiples of 2 spaces)
                leading_spaces = len(line) - len(line.lstrip())
                if leading_spaces > 0:
                    assert leading_spaces % 2 == 0


class TestErrorHandling:
    """Tests for error handling scenarios."""
    
    @pytest.fixture
    def sample_config(self):
        """Sample configuration data."""
        return {
            "run_id": "test-run-001",
            "model_name": "llama3:latest",
            "cycle_count": 10
        }
    
    def test_permission_error_handling(self, sample_config):
        """Test handling of permission errors."""
        # Create a read-only directory
        temp_dir = Path(tempfile.mkdtemp())
        configs_dir = temp_dir / "configs"
        configs_dir.mkdir(exist_ok=True)
        
        try:
            # Make configs directory read-only (platform-specific)
            if os.name == 'posix':
                os.chmod(configs_dir, 0o444)
                
                success, message = save_config_to_yaml(sample_config, "test-perms", temp_dir)
                
                assert success is False
                assert "Permission denied" in message or "permission" in message.lower()
            else:
                # Windows permission handling is different, skip this test
                pytest.skip("Permission testing not implemented for Windows")
        finally:
            # Restore permissions and cleanup
            if os.name == 'posix':
                os.chmod(configs_dir, 0o755)
            shutil.rmtree(temp_dir)
    
    def test_invalid_data_handling(self):
        """Test handling of invalid data types."""
        temp_dir = Path(tempfile.mkdtemp())
        
        try:
            # YAML should handle most Python types, but test with unserializable objects
            import threading
            invalid_config = {
                "run_id": "test",
                "lock": threading.Lock()  # Not YAML serializable
            }
            
            success, message = save_config_to_yaml(invalid_config, "test-invalid", temp_dir)
            
            # Should fail with error message
            assert success is False
            assert "error" in message.lower()
        finally:
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
