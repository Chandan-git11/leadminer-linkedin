"""Unit tests for config module."""
import pytest
from pathlib import Path
import sys
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import Config


class TestConfig:
    """Test cases for Config."""

    def test_config_defaults(self):
        """Test config has reasonable defaults."""
        assert Config.LOG_LEVEL in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        assert Config.BROWSER_TIMEOUT > 0
        assert Config.WAIT_FOR_LOAD_TIME > 0
        assert Config.MAX_SCROLLS > 0
        assert Config.SCROLL_DELAY > 0

    def test_validate_missing_credentials(self):
        """Test validation fails without credentials."""
        # Temporarily clear credentials
        original_email = Config.LINKEDIN_EMAIL
        original_password = Config.LINKEDIN_PASSWORD

        Config.LINKEDIN_EMAIL = ""
        Config.LINKEDIN_PASSWORD = ""

        assert Config.validate() is False

        # Restore
        Config.LINKEDIN_EMAIL = original_email
        Config.LINKEDIN_PASSWORD = original_password

    def test_get_session_file_default(self):
        """Test getting default session file."""
        session_file = Config.get_session_file()

        assert session_file.name == "default_session.json"

    def test_get_session_file_with_username(self):
        """Test getting session file with username."""
        session_file = Config.get_session_file("john.doe")

        assert session_file.name == "john.doe_session.json"

    def test_ensure_output_dir_creates_dir(self):
        """Test ensure_output_dir creates directory."""
        output_dir = Config.ensure_output_dir()

        assert output_dir.exists()
        assert output_dir.is_dir()

    def test_ensure_log_dir_creates_dir(self):
        """Test ensure_log_dir creates directory."""
        log_dir = Config.ensure_log_dir()

        assert log_dir.exists()
        assert log_dir.is_dir()

    def test_session_storage_path_creation(self):
        """Test session storage directory is created."""
        session_file = Config.get_session_file()

        assert session_file.parent.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
