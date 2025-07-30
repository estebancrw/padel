"""Unit tests for configuration management."""

import json
import os
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from src.config import (
    get_bot_token,
    get_chat_id,
    get_config_path,
    get_data_dir,
    get_force_week,
    get_project_root,
    get_schedule_path,
    get_test_message,
    load_config,
)


class TestConfigLoading:
    """Test configuration file loading."""

    def test_load_config_valid_json(self):
        """Test loading valid JSON configuration."""
        mock_json = json.dumps(
            {"timezone": "America/Mexico_City", "message_template": "Hello {name}!"}
        )

        with patch("builtins.open", mock_open(read_data=mock_json)):
            config = load_config(Path("mock_config.json"))
            assert config["timezone"] == "America/Mexico_City"
            assert config["message_template"] == "Hello {name}!"

    def test_load_config_invalid_json(self):
        """Test loading invalid JSON raises error."""
        with patch("builtins.open", mock_open(read_data="{ invalid json")):
            with pytest.raises(json.JSONDecodeError):
                load_config(Path("mock_config.json"))


class TestEnvironmentVariables:
    """Test environment variable handling."""

    def test_get_bot_token_exists(self):
        """Test getting bot token when it exists."""
        with patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "test-token-123"}):
            assert get_bot_token() == "test-token-123"

    def test_get_bot_token_missing(self):
        """Test getting bot token when missing raises error."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="TELEGRAM_BOT_TOKEN"):
                get_bot_token()

    def test_get_chat_id_exists(self):
        """Test getting chat ID when it exists."""
        with patch.dict(os.environ, {"TELEGRAM_CHAT_ID": "-123456789"}):
            assert get_chat_id() == "-123456789"

    def test_get_chat_id_missing(self):
        """Test getting chat ID when missing raises error."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="TELEGRAM_CHAT_ID"):
                get_chat_id()

    def test_get_test_message_exists(self):
        """Test getting test message override."""
        with patch.dict(os.environ, {"TEST_MESSAGE": "Test message"}):
            assert get_test_message() == "Test message"

    def test_get_test_message_missing(self):
        """Test getting test message when not set."""
        with patch.dict(os.environ, {}, clear=True):
            assert get_test_message() is None

    def test_get_force_week_valid(self):
        """Test forcing a specific week number."""
        with patch.dict(os.environ, {"FORCE_WEEK": "42"}):
            assert get_force_week() == "2025-W42"

    def test_get_force_week_with_padding(self):
        """Test force week with single digit gets padded."""
        with patch.dict(os.environ, {"FORCE_WEEK": "5"}):
            assert get_force_week() == "2025-W05"

    def test_get_force_week_invalid(self):
        """Test invalid force week returns None."""
        with patch.dict(os.environ, {"FORCE_WEEK": "not-a-number"}):
            assert get_force_week() is None

    def test_get_force_week_missing(self):
        """Test missing force week returns None."""
        with patch.dict(os.environ, {}, clear=True):
            assert get_force_week() is None


class TestPathHelpers:
    """Test path helper functions."""

    def test_get_project_root(self):
        """Test project root path calculation."""
        root = get_project_root()
        # Should be parent of src directory
        assert root.name == "padel"
        assert (root / "src").exists()

    def test_get_data_dir(self):
        """Test data directory path."""
        data_dir = get_data_dir()
        assert data_dir.name == "data"
        assert data_dir.parent == get_project_root()

    def test_get_schedule_path(self):
        """Test schedule file path."""
        schedule_path = get_schedule_path()
        assert schedule_path.name == "schedule_2025.json"
        assert schedule_path.parent == get_data_dir()

    def test_get_config_path(self):
        """Test config file path."""
        config_path = get_config_path()
        assert config_path.name == "config.json"
        assert config_path.parent == get_data_dir()

    def test_paths_are_consistent(self):
        """Test that all paths are consistent with each other."""
        root = get_project_root()
        data = get_data_dir()
        schedule = get_schedule_path()
        config = get_config_path()

        assert data == root / "data"
        assert schedule == data / "schedule_2025.json"
        assert config == data / "config.json"


class TestIntegration:
    """Test integration with actual files."""

    def test_actual_config_file_exists(self):
        """Test that actual config file exists and is valid."""
        config_path = get_config_path()
        assert config_path.exists(), f"Config file not found at {config_path}"

        # Try to load it
        config = load_config(config_path)
        assert "timezone" in config
        assert "message_template" in config
        assert "schedule" in config

    def test_actual_schedule_file_exists(self):
        """Test that actual schedule file exists."""
        schedule_path = get_schedule_path()
        assert schedule_path.exists(), f"Schedule file not found at {schedule_path}"
