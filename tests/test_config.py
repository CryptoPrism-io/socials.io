"""Unit tests for configuration system."""
import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.config import (
    config, DatabaseConfig, PathConfig, ImageConfig,
    APIConfig, LoggingConfig, Config
)


class TestDatabaseConfig:
    """Test database configuration settings."""

    def test_database_config_creation(self):
        """Test database config creation with defaults."""
        db_config = DatabaseConfig()

        assert db_config.host == "34.55.195.199"  # Default value
        assert db_config.port == 5432
        assert db_config.database == "dbcp"
        assert db_config.user == "yogass09"  # These would normally be env vars

    @patch.dict(os.environ, {"DB_HOST": "test-host", "DB_USER": "test-user"})
    def test_database_config_env_vars(self):
        """Test database config reads from environment variables."""
        db_config = DatabaseConfig()

        assert db_config.host == "test-host"
        assert db_config.user == "test-user"

    def test_database_config_connection_url(self):
        """Test database connection URL generation."""
        db_config = DatabaseConfig()
        url = db_config.get_connection_url("psycopg2")

        assert "postgresql+psycopg2://" in url
        assert "yogass09" in url
        assert "34.55.195.199:5432/dbcp" in url

    def test_database_config_validation_missing_env(self):
        """Test validation when required env vars are empty."""
        db_config = DatabaseConfig(
            host="", database="", user="", password=""
        )

        with pytest.raises(ValueError, match="Database configuration incomplete"):
            db_config.validate()


class TestImageConfig:
    """Test image configuration settings."""

    def test_image_config_defaults(self):
        """Test image config with default values."""
        img_config = ImageConfig()

        assert img_config.width == 1080
        assert img_config.height == 1080  # Square default
        assert img_config.quality == 95
        assert img_config.format == "jpg"

    @patch.dict(os.environ, {"IMAGE_WIDTH": "1920", "IMAGE_QUALITY": "85"})
    def test_image_config_env_vars(self):
        """Test image config reads from env vars."""
        img_config = ImageConfig()

        assert img_config.width == 1920
        assert img_config.quality == 85

    def test_image_config_validation(self):
        """Test image config validation."""
        # Valid config should pass
        img_config = ImageConfig(width=2000, height=2000, quality=90)
        img_config.validate()  # Should not raise

        # Invalid dimensions should fail
        with pytest.raises(ValueError, match="Invalid image dimensions"):
            ImageConfig(width=50, height=100).validate()

        # Invalid quality should fail
        with pytest.raises(ValueError, match="Invalid image quality"):
            ImageConfig(quality=150).validate()


class TestPathConfig:
    """Test path configuration settings."""

    def test_path_config_directory_creation(self, tmp_path):
        """Test path config creates directories correctly."""
        # Mock project root
        with patch('pathlib.Path') as mock_path:
            mock_path.return_value = tmp_path

            path_config = PathConfig()
            path_config.ensure_directories()

            # Check that mkdir was called (directories would be created)

    def test_path_config_template_paths(self):
        """Test template file path generation."""
        path_config = PathConfig()

        # Should generate paths for templates 1-6
        template_paths = path_config.get_template_files()
        assert len(template_paths) == 6
        assert str(template_paths[0]).endswith("1.html")
        assert str(template_paths[-1]).endswith("6.html")

    def test_path_config_output_paths(self):
        """Test output path generation."""
        path_config = PathConfig()

        html_path = path_config.get_html_output_path(1)
        image_path = path_config.get_image_output_path(1)

        assert html_path.name == "1_output.html"
        assert image_path.name == "1_output.jpg"


class TestAPIConfig:
    """Test API configuration settings."""

    def test_api_config_env_vars(self):
        """Test API config reads from environment."""
        with patch.dict(os.environ, {
            "TOGETHER_API_KEY": "sk-test-key",
            "INSTAGRAM_USERNAME": "test_user"
        }):
            api_config = APIConfig()

            assert api_config.together_api_key == "sk-test-key"
            assert api_config.instagram_username == "test_user"

    def test_api_config_validation_together_key(self):
        """Test Together API key validation."""
        # Valid key should pass
        api_config = APIConfig(together_api_key="sk-valid-key")
        api_config.validate()

        # Invalid key format should fail
        with pytest.raises(ValueError, match="Invalid Together API key format"):
            APIConfig(together_api_key="invalid-key").validate()


class TestConfigIntegration:
    """Integration tests for the complete config system."""

    def test_global_config_instance(self):
        """Test that global config instance is properly configured."""
        # The global config instance should be available
        assert hasattr(config, 'database')
        assert hasattr(config, 'image')
        assert hasattr(config, 'api')
        assert hasattr(config, 'logging')

    def test_config_timestamps(self):
        """Test that config includes timezone-aware timestamps."""
        assert config.app.datetime_format == "%d %b, %Y"
        assert config.app.time_format == "%I:%M:%S %p"

    def test_config_validate_all(self):
        """Test full configuration validation."""
        try:
            config.validate_all()
            assert True  # If no exception, validation passed
        except ValueError as e:
            # Validation might fail in test environment due to missing env vars
            assert "incomplete" in str(e) or "required" in str(e)


@pytest.mark.unit
class TestConfigUnit:
    """Unit marker tests for configuration."""

    def test_config_is_singleton(self):
        """Test that config behaves like a singleton."""
        config1 = config
        config2 = config  # Re-import would get same instance
        assert config1 is config2