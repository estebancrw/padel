#!/usr/bin/env python3
"""Main bot script for sending padel rotation reminders."""

import argparse
import asyncio
import logging
import sys

from telegram import Bot
from telegram.error import TelegramError

from src.config import (
    get_bot_token,
    get_chat_id,
    get_config_path,
    get_force_week,
    get_schedule_path,
    get_test_message,
    load_config,
)
from src.rotation import (
    format_message,
    get_current_week_string,
    get_responsible_person,
    load_schedule_data,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def send_message(
    bot: Bot, chat_id: str, message: str, dry_run: bool = False
) -> bool:
    """Send message to Telegram chat."""
    if dry_run:
        logger.info(f"[DRY RUN] Would send message to {chat_id}:")
        logger.info(f"[DRY RUN] {message}")
        return True

    try:
        await bot.send_message(chat_id=chat_id, text=message)
        logger.info(f"Message sent successfully to {chat_id}")
        return True
    except (TelegramError, Exception) as e:
        logger.error(f"Failed to send message: {e}")
        return False


async def main(args: argparse.Namespace) -> int:
    """Main bot logic."""
    try:
        # Load configuration
        config = load_config(get_config_path())
        schedule_data = load_schedule_data(get_schedule_path())

        # Get bot credentials
        if not args.dry_run:
            bot_token = get_bot_token()
            chat_id = get_chat_id()
            bot = Bot(token=bot_token)
        else:
            bot = None
            chat_id = "TEST_CHAT_ID"

        # Determine week to use
        if args.test_week:
            week_string = f"2025-W{args.test_week:02d}"
            logger.info(f"Using test week: {week_string}")
        elif force_week := get_force_week():
            week_string = force_week
            logger.info(f"Using forced week: {week_string}")
        else:
            week_string = get_current_week_string(config["timezone"])
            logger.info(f"Using current week: {week_string}")

        # Get responsible person
        responsible_person, special_message = get_responsible_person(
            week_string, schedule_data
        )
        logger.info(f"Responsible person for {week_string}: {responsible_person}")

        # Format message
        test_message = get_test_message()
        if test_message:
            message = test_message
            logger.info("Using test message override")
        else:
            message = format_message(
                config["message_template"],
                responsible_person,
                week_string,
                special_message,
            )

        # Send message
        if bot:
            success = await send_message(bot, chat_id, message, args.dry_run)
            return 0 if success else 1
        else:
            # Dry run - no bot needed
            logger.info(f"[DRY RUN] Would send message to {chat_id}:")
            logger.info(f"[DRY RUN] {message}")
            return 0

    except Exception as e:
        logger.error(f"Bot error: {e}")
        return 1


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Padel Bot - Send rotation reminders to Telegram group"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print message instead of sending to Telegram",
    )
    parser.add_argument(
        "--test-week",
        type=int,
        help="Test with specific week number (1-52)",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run in test mode (implies --dry-run)",
    )
    return parser


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()

    # Test mode implies dry run
    if args.test:
        args.dry_run = True

    # Run the bot
    exit_code = asyncio.run(main(args))
    sys.exit(exit_code)
