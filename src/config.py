"""Configuration management for the bot."""

import json
import os
from pathlib import Path
from typing import Optional


def load_config(config_path: Path) -> dict:
    """Load bot configuration from JSON file."""
    with open(config_path, encoding="utf-8") as f:
        return json.load(f)  # type: ignore[no-any-return]


def get_bot_token() -> str:
    """Get bot token from environment variable."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")
    return token


def get_chat_id() -> str:
    """Get chat ID from environment variable."""
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not chat_id:
        raise ValueError("TELEGRAM_CHAT_ID environment variable not set")
    return chat_id


def get_test_message() -> Optional[str]:
    """Get test message override from environment variable."""
    return os.environ.get("TEST_MESSAGE")


def get_force_week() -> Optional[str]:
    """Get forced week number from environment variable."""
    force_week = os.environ.get("FORCE_WEEK")
    if force_week:
        try:
            week_num = int(force_week)
            return f"2025-W{week_num:02d}"
        except ValueError:
            return None
    return None


def get_project_root() -> Path:
    """Get the project root directory."""
    # Navigate from src/config.py to project root
    return Path(__file__).parent.parent


def get_data_dir() -> Path:
    """Get the data directory path."""
    return get_project_root() / "data"


def get_schedule_path() -> Path:
    """Get the schedule JSON file path."""
    return get_data_dir() / "schedule_2025.json"


def get_config_path() -> Path:
    """Get the config JSON file path."""
    return get_data_dir() / "config.json"
