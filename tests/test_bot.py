"""Unit tests for the main bot functionality."""

import argparse
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.bot import create_parser, main, send_message


class TestSendMessage:
    """Test message sending functionality."""

    @pytest.mark.asyncio
    async def test_send_message_success(self):
        """Test successful message sending."""
        mock_bot = AsyncMock()
        mock_bot.send_message.return_value = MagicMock()

        result = await send_message(mock_bot, "12345", "Test message")

        assert result is True
        mock_bot.send_message.assert_called_once_with(
            chat_id="12345", text="Test message"
        )

    @pytest.mark.asyncio
    async def test_send_message_failure(self):
        """Test message sending with Telegram error."""
        mock_bot = AsyncMock()
        mock_bot.send_message.side_effect = Exception("Network error")

        result = await send_message(mock_bot, "12345", "Test message")

        assert result is False

    @pytest.mark.asyncio
    async def test_send_message_dry_run(self):
        """Test dry run mode doesn't send actual message."""
        mock_bot = AsyncMock()

        result = await send_message(mock_bot, "12345", "Test message", dry_run=True)

        assert result is True
        mock_bot.send_message.assert_not_called()


class TestMainFunction:
    """Test the main bot function."""

    @pytest.fixture
    def mock_config(self):
        """Mock configuration data."""
        return {
            "timezone": "America/Mexico_City",
            "message_template": "Week {week}: {name} is responsible!",
        }

    @pytest.fixture
    def mock_schedule(self):
        """Mock schedule data."""
        return {
            "default_rotation": ["Esteban", "Chema", "Adrian"],
            "start_week": "2025-W31",
            "schedule_overrides": {},
            "vacation_weeks": {},
            "special_messages": {},
        }

    @pytest.mark.asyncio
    async def test_main_success(self, mock_config, mock_schedule):
        """Test successful main execution."""
        args = argparse.Namespace(dry_run=False, test_week=None, test=False)

        with (
            patch("src.bot.load_config", return_value=mock_config),
            patch("src.bot.load_schedule_data", return_value=mock_schedule),
            patch("src.bot.get_bot_token", return_value="test-token"),
            patch("src.bot.get_chat_id", return_value="test-chat"),
            patch("src.bot.get_current_week_string", return_value="2025-W31"),
            patch("src.bot.Bot") as MockBot,
            patch("src.bot.send_message", return_value=True) as mock_send,
        ):
            result = await main(args)

            assert result == 0
            MockBot.assert_called_once_with(token="test-token")
            mock_send.assert_called_once()

    @pytest.mark.asyncio
    async def test_main_dry_run(self, mock_config, mock_schedule):
        """Test main execution in dry run mode."""
        args = argparse.Namespace(dry_run=True, test_week=None, test=False)

        with (
            patch("src.bot.load_config", return_value=mock_config),
            patch("src.bot.load_schedule_data", return_value=mock_schedule),
            patch("src.bot.get_current_week_string", return_value="2025-W31"),
            patch("src.bot.Bot") as MockBot,
        ):
            result = await main(args)

            assert result == 0
            MockBot.assert_not_called()  # No bot created in dry run

    @pytest.mark.asyncio
    async def test_main_with_test_week(self, mock_config, mock_schedule):
        """Test main execution with specific test week."""
        args = argparse.Namespace(dry_run=True, test_week=42, test=False)

        with (
            patch("src.bot.load_config", return_value=mock_config),
            patch("src.bot.load_schedule_data", return_value=mock_schedule),
            patch(
                "src.bot.get_responsible_person", return_value=("TestPerson", None)
            ) as mock_responsible,
        ):
            result = await main(args)

            assert result == 0
            mock_responsible.assert_called_with("2025-W42", mock_schedule)

    @pytest.mark.asyncio
    async def test_main_with_force_week(self, mock_config, mock_schedule):
        """Test main execution with forced week from environment."""
        args = argparse.Namespace(dry_run=True, test_week=None, test=False)

        with (
            patch("src.bot.load_config", return_value=mock_config),
            patch("src.bot.load_schedule_data", return_value=mock_schedule),
            patch("src.bot.get_force_week", return_value="2025-W35"),
            patch(
                "src.bot.get_responsible_person", return_value=("ForcedPerson", None)
            ) as mock_responsible,
        ):
            result = await main(args)

            assert result == 0
            mock_responsible.assert_called_with("2025-W35", mock_schedule)

    @pytest.mark.asyncio
    async def test_main_with_test_message(self, mock_config, mock_schedule):
        """Test main execution with test message override."""
        args = argparse.Namespace(dry_run=True, test_week=None, test=False)

        test_msg = "This is a test message!"

        with (
            patch("src.bot.load_config", return_value=mock_config),
            patch("src.bot.load_schedule_data", return_value=mock_schedule),
            patch("src.bot.get_current_week_string", return_value="2025-W31"),
            patch("src.bot.get_test_message", return_value=test_msg),
        ):
            # Since it's dry run, we just need to verify it doesn't crash
            result = await main(args)
            assert result == 0

    @pytest.mark.asyncio
    async def test_main_error_handling(self, mock_config, mock_schedule):
        """Test main handles errors gracefully."""
        args = argparse.Namespace(dry_run=False, test_week=None, test=False)

        with patch("src.bot.load_config", side_effect=Exception("Config error")):
            result = await main(args)
            assert result == 1  # Error exit code


class TestArgumentParser:
    """Test command line argument parsing."""

    def test_create_parser(self):
        """Test parser creation."""
        parser = create_parser()
        assert isinstance(parser, argparse.ArgumentParser)

    def test_parse_dry_run(self):
        """Test parsing dry run flag."""
        parser = create_parser()
        args = parser.parse_args(["--dry-run"])
        assert args.dry_run is True
        assert args.test_week is None
        assert args.test is False

    def test_parse_test_week(self):
        """Test parsing test week."""
        parser = create_parser()
        args = parser.parse_args(["--test-week", "25"])
        assert args.test_week == 25
        assert args.dry_run is False

    def test_parse_test_mode(self):
        """Test parsing test mode."""
        parser = create_parser()
        args = parser.parse_args(["--test"])
        assert args.test is True

    def test_parse_multiple_args(self):
        """Test parsing multiple arguments."""
        parser = create_parser()
        args = parser.parse_args(["--dry-run", "--test-week", "10"])
        assert args.dry_run is True
        assert args.test_week == 10

    def test_parse_no_args(self):
        """Test parsing with no arguments."""
        parser = create_parser()
        args = parser.parse_args([])
        assert args.dry_run is False
        assert args.test_week is None
        assert args.test is False


class TestIntegration:
    """Integration tests with actual components."""

    @pytest.mark.asyncio
    async def test_full_flow_dry_run(self):
        """Test complete flow in dry run mode."""
        args = argparse.Namespace(dry_run=True, test_week=31, test=False)

        # This should work with actual config files
        result = await main(args)
        assert result == 0
