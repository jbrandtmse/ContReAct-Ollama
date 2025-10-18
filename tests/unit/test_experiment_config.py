"""
Unit tests for ExperimentConfig dataclass and validation.

Part of: Story 3.1 - Telegram Configuration (Backend & UI)
"""
import os
import pytest
from unittest.mock import patch

from contreact_ollama.core.config import ExperimentConfig, InvalidConfigurationError


@pytest.fixture
def base_config():
    """Provide base ExperimentConfig without Telegram fields."""
    return {
        "run_id": "test-run",
        "model_name": "llama3:latest",
        "cycle_count": 10,
        "ollama_client_config": {"host": "http://localhost:11434"},
        "model_options": {"temperature": 0.7}
    }


@pytest.fixture
def telegram_config():
    """Provide sample Telegram configuration for testing."""
    return {
        "telegram_enabled": True,
        "telegram_authorized_users": [123456789],
        "telegram_timeout_minutes": 5
    }


class TestExperimentConfigDefaults:
    """Test default values for Telegram fields."""
    
    def test_telegram_disabled_by_default(self, base_config):
        """Test that Telegram is disabled by default."""
        config = ExperimentConfig(**base_config)
        assert config.telegram_enabled is False
    
    def test_telegram_bot_token_none_by_default(self, base_config):
        """Test that bot token is None by default."""
        config = ExperimentConfig(**base_config)
        assert config.telegram_bot_token is None
    
    def test_telegram_authorized_users_empty_by_default(self, base_config):
        """Test that authorized users list is empty by default."""
        config = ExperimentConfig(**base_config)
        assert config.telegram_authorized_users == []
    
    def test_telegram_timeout_default_value(self, base_config):
        """Test that default timeout is 5 minutes."""
        config = ExperimentConfig(**base_config)
        assert config.telegram_timeout_minutes == 5


class TestExperimentConfigTelegramFields:
    """Test ExperimentConfig with Telegram fields."""
    
    def test_create_config_with_telegram_enabled(self, base_config, telegram_config):
        """Test creating config with Telegram enabled."""
        config_data = {**base_config, **telegram_config}
        config = ExperimentConfig(**config_data)
        
        assert config.telegram_enabled is True
        assert config.telegram_authorized_users == [123456789]
        assert config.telegram_timeout_minutes == 5
    
    def test_create_config_with_multiple_users(self, base_config):
        """Test creating config with multiple authorized users."""
        config_data = {
            **base_config,
            "telegram_enabled": True,
            "telegram_authorized_users": [123456789, 987654321, 555555555]
        }
        config = ExperimentConfig(**config_data)
        
        assert len(config.telegram_authorized_users) == 3
        assert 123456789 in config.telegram_authorized_users
        assert 987654321 in config.telegram_authorized_users
        assert 555555555 in config.telegram_authorized_users
    
    def test_create_config_with_timeout_minus_one(self, base_config, telegram_config):
        """Test creating config with -1 timeout (wait forever)."""
        config_data = {**base_config, **telegram_config}
        config_data["telegram_timeout_minutes"] = -1
        config = ExperimentConfig(**config_data)
        
        assert config.telegram_timeout_minutes == -1
    
    def test_create_config_with_timeout_zero(self, base_config, telegram_config):
        """Test creating config with 0 timeout (immediate)."""
        config_data = {**base_config, **telegram_config}
        config_data["telegram_timeout_minutes"] = 0
        config = ExperimentConfig(**config_data)
        
        assert config.telegram_timeout_minutes == 0
    
    def test_create_config_with_timeout_max(self, base_config, telegram_config):
        """Test creating config with maximum timeout (120 minutes)."""
        config_data = {**base_config, **telegram_config}
        config_data["telegram_timeout_minutes"] = 120
        config = ExperimentConfig(**config_data)
        
        assert config.telegram_timeout_minutes == 120


class TestTelegramConfigValidation:
    """Test Telegram configuration validation logic."""
    
    @patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "test_token"})
    def test_validate_telegram_config_enabled_with_token_succeeds(
        self, base_config, telegram_config
    ):
        """Test that validation succeeds when Telegram enabled with token set."""
        config_data = {**base_config, **telegram_config}
        config = ExperimentConfig(**config_data)
        
        # Should not raise any exception
        config.validate_telegram_config()
    
    @patch.dict(os.environ, {}, clear=True)
    def test_validate_telegram_config_enabled_no_token_raises_error(
        self, base_config, telegram_config
    ):
        """Test that validation raises error when Telegram enabled but no token."""
        config_data = {**base_config, **telegram_config}
        config = ExperimentConfig(**config_data)
        
        with pytest.raises(InvalidConfigurationError) as exc_info:
            config.validate_telegram_config()
        
        assert "TELEGRAM_BOT_TOKEN environment variable not set" in str(exc_info.value)
    
    @patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "test_token"})
    def test_validate_telegram_config_enabled_no_users_raises_error(self, base_config):
        """Test that validation raises error when Telegram enabled but no users."""
        config_data = {
            **base_config,
            "telegram_enabled": True,
            "telegram_authorized_users": [],
            "telegram_timeout_minutes": 5
        }
        config = ExperimentConfig(**config_data)
        
        with pytest.raises(InvalidConfigurationError) as exc_info:
            config.validate_telegram_config()
        
        assert "no authorized users configured" in str(exc_info.value)
    
    @patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "test_token"})
    def test_validate_telegram_config_timeout_below_minimum_raises_error(
        self, base_config, telegram_config
    ):
        """Test that validation raises error for timeout < -1."""
        config_data = {**base_config, **telegram_config}
        config_data["telegram_timeout_minutes"] = -2
        config = ExperimentConfig(**config_data)
        
        with pytest.raises(InvalidConfigurationError) as exc_info:
            config.validate_telegram_config()
        
        assert "must be -1 (wait forever) or between 0 and 120" in str(exc_info.value)
    
    @patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "test_token"})
    def test_validate_telegram_config_timeout_above_maximum_raises_error(
        self, base_config, telegram_config
    ):
        """Test that validation raises error for timeout > 120."""
        config_data = {**base_config, **telegram_config}
        config_data["telegram_timeout_minutes"] = 121
        config = ExperimentConfig(**config_data)
        
        with pytest.raises(InvalidConfigurationError) as exc_info:
            config.validate_telegram_config()
        
        assert "must be -1 (wait forever) or between 0 and 120" in str(exc_info.value)
    
    def test_validate_telegram_config_disabled_no_validation(self, base_config):
        """Test that validation is skipped when Telegram is disabled."""
        config_data = {
            **base_config,
            "telegram_enabled": False,
            "telegram_authorized_users": [],
            "telegram_timeout_minutes": 999  # Invalid value, but should not raise
        }
        config = ExperimentConfig(**config_data)
        
        # Should not raise any exception since Telegram is disabled
        config.validate_telegram_config()
    
    @patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "test_token"})
    def test_validate_telegram_config_timeout_boundary_values(
        self, base_config, telegram_config
    ):
        """Test validation with boundary timeout values."""
        # Test -1 (minimum valid)
        config_data = {**base_config, **telegram_config}
        config_data["telegram_timeout_minutes"] = -1
        config = ExperimentConfig(**config_data)
        config.validate_telegram_config()  # Should not raise
        
        # Test 0 (boundary)
        config_data["telegram_timeout_minutes"] = 0
        config = ExperimentConfig(**config_data)
        config.validate_telegram_config()  # Should not raise
        
        # Test 120 (maximum valid)
        config_data["telegram_timeout_minutes"] = 120
        config = ExperimentConfig(**config_data)
        config.validate_telegram_config()  # Should not raise


class TestBackwardCompatibility:
    """Test backward compatibility with existing configs."""
    
    def test_load_config_without_telegram_fields(self, base_config):
        """Test that existing configs without Telegram fields load correctly."""
        # Old config files won't have Telegram fields
        config = ExperimentConfig(**base_config)
        
        # Should use default values
        assert config.telegram_enabled is False
        assert config.telegram_authorized_users == []
        assert config.telegram_timeout_minutes == 5
    
    def test_validate_old_config_succeeds(self, base_config):
        """Test that validation succeeds for old configs without Telegram."""
        config = ExperimentConfig(**base_config)
        
        # Should not raise any exception
        config.validate_telegram_config()


class TestInvalidConfigurationError:
    """Test InvalidConfigurationError exception."""
    
    def test_invalid_configuration_error_is_exception(self):
        """Test that InvalidConfigurationError is an Exception."""
        error = InvalidConfigurationError("test message")
        assert isinstance(error, Exception)
    
    def test_invalid_configuration_error_message(self):
        """Test that error message is preserved."""
        message = "Test error message"
        error = InvalidConfigurationError(message)
        assert str(error) == message
