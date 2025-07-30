# Padel Bot Setup Guide

This guide covers everything you need to set up the Padel Bot from scratch.

## Table of Contents
1. [Creating a Telegram Bot](#creating-a-telegram-bot)
2. [Getting the Chat ID](#getting-the-chat-id)
3. [Setting up GitHub Secrets](#setting-up-github-secrets)
4. [Local Development](#local-development)
5. [Testing](#testing)
6. [Deployment](#deployment)
7. [Troubleshooting](#troubleshooting)

## Creating a Telegram Bot

### Step 1: Talk to BotFather

1. Open Telegram and search for `@BotFather`
2. Start a conversation by clicking "Start"
3. Send the command `/newbot`
4. BotFather will ask for:
   - **Bot name**: A display name (e.g., "Padel Court Reminder")
   - **Bot username**: Must end in 'bot' (e.g., "PadelCourtReminderBot")

### Step 2: Save Your Bot Token

BotFather will respond with:
```
Done! Congratulations on your new bot. You will find it at t.me/YourBotName.

Use this token to access the HTTP API:
5678901234:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi

Keep your token secure and store it safely!
```

**⚠️ IMPORTANT**: Save this token! You'll need it for `TELEGRAM_BOT_TOKEN`.

### Step 3: Configure Bot Settings (Optional)

Send these commands to BotFather to configure your bot:
- `/setdescription` - Set bot description
- `/setabouttext` - Set about text
- `/setuserpic` - Set bot profile picture

## Getting the Chat ID

### Method 1: Using the Bot (Recommended)

1. **Create a Telegram group** for your padel team
2. **Add your bot** to the group:
   - Open group info → Add Member → Search for your bot → Add
3. **Make the bot admin** (required for it to read messages):
   - Group Info → Administrators → Add Administrator → Select your bot
4. **Send a test message** in the group (e.g., "Hello bot!")
5. **Get the chat ID** using your browser:
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
   Replace `<YOUR_BOT_TOKEN>` with your actual token.

6. **Find the chat ID** in the response:
   ```json
   {
     "ok": true,
     "result": [{
       "message": {
         "chat": {
           "id": -123456789,  // This is your TELEGRAM_CHAT_ID
           "title": "Padel Group",
           "type": "group"
         }
       }
     }]
   }
   ```

**Note**: Group chat IDs are negative numbers (e.g., `-123456789`).

### Method 2: Using a Bot Command

Alternatively, you can temporarily add this code to get the chat ID:

```python
# temporary_get_chat_id.py
import asyncio
from telegram import Bot

async def get_chat_id():
    bot = Bot(token="YOUR_BOT_TOKEN")
    updates = await bot.get_updates()
    for update in updates:
        if update.message:
            print(f"Chat ID: {update.message.chat_id}")
            print(f"Chat Title: {update.message.chat.title}")

asyncio.run(get_chat_id())
```

## Setting up GitHub Secrets

### Required Secrets

You need to add these two secrets to your GitHub repository:

1. **TELEGRAM_BOT_TOKEN**: The token from BotFather
2. **TELEGRAM_CHAT_ID**: The group chat ID (negative number)

### How to Add Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret:
   - Name: `TELEGRAM_BOT_TOKEN`
   - Value: `5678901234:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi`
5. Repeat for:
   - Name: `TELEGRAM_CHAT_ID`
   - Value: `-123456789`

## Local Development

### Prerequisites

- Python 3.9+
- [uv](https://github.com/astral-sh/uv) package manager

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/padel-bot.git
   cd padel-bot
   ```

2. **Install dependencies**:
   ```bash
   uv sync --all-extras
   ```

3. **Set environment variables**:
   ```bash
   export TELEGRAM_BOT_TOKEN="your_bot_token"
   export TELEGRAM_CHAT_ID="your_chat_id"
   ```

   Or create a `.env` file (don't commit this!):
   ```env
   TELEGRAM_BOT_TOKEN=5678901234:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi
   TELEGRAM_CHAT_ID=-123456789
   ```

### Running Locally

```bash
# Dry run (no actual message sent)
uv run python src/bot.py --dry-run

# Test specific week
uv run python src/bot.py --dry-run --test-week 31

# Send actual message (be careful!)
uv run python src/bot.py
```

## Testing

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov

# Run specific test file
uv run pytest tests/test_rotation.py

# Run with verbose output
uv run pytest -v
```

### Linting and Type Checking

```bash
# Run linter
uv run ruff check src/ tests/

# Fix linting issues
uv run ruff check --fix src/ tests/

# Type checking
uv run mypy src/
```

### Manual Testing Checklist

Before deploying:

- [ ] Test with `--dry-run` for current week
- [ ] Test rotation for next 6 weeks
- [ ] Verify message format looks correct
- [ ] Test with actual bot token (in test group first!)
- [ ] Verify GitHub Actions workflow syntax

## Deployment

### GitHub Actions Setup

The bot runs automatically via GitHub Actions. The workflow is already configured in `.github/workflows/send-message.yml`.

### Manual Trigger

You can manually trigger the bot:

1. Go to **Actions** tab in GitHub
2. Select **Send Padel Message** workflow
3. Click **Run workflow**
4. Optionally set test parameters
5. Click **Run workflow** (green button)

### Monitoring

- Check **Actions** tab for execution history
- Failed runs will send email notifications
- Review logs for any errors

## Troubleshooting

### Common Issues

#### "TELEGRAM_BOT_TOKEN environment variable not set"
- Make sure you've added the secret to GitHub
- For local testing, ensure you've exported the variable

#### "Chat not found"
- Verify the chat ID is correct (should be negative for groups)
- Ensure the bot is added to the group
- Check that the bot has admin permissions

#### "Forbidden: bot was kicked from the group chat"
- Re-add the bot to the group
- Make sure to make it an admin

#### Message not sending on schedule
- Check GitHub Actions is enabled for the repository
- Verify the cron schedule in the workflow file
- Check Actions tab for any failed runs

#### Rate limit errors
- The bot implements automatic retry with backoff
- If persistent, check if someone else is using the bot token

### Debug Mode

For detailed logging, run locally with:

```bash
uv run python src/bot.py --dry-run --test-week 31
```

This will show:
- Which week is being used
- Who is responsible
- The exact message that would be sent

### Getting Help

1. Check the logs in GitHub Actions
2. Run tests locally to reproduce issues
3. Check that your rotation JSON is valid
4. Verify environment variables are set correctly

## Security Best Practices

1. **Never commit tokens**: Use GitHub Secrets
2. **Rotate tokens regularly**: Every 30-90 days
3. **Use test groups first**: Don't test in production
4. **Limit bot permissions**: Only give necessary permissions
5. **Monitor usage**: Check for unauthorized access

## Advanced Configuration

### Custom Message Templates

Edit `data/config.json` to customize messages:

```json
{
  "message_template": "🎾 Custom message for {name} in week {week}!"
}
```

### Holiday Handling

Add special messages in `data/schedule_2025.json`:

```json
{
  "special_messages": {
    "2025-W52": "🎄 {name} - Remember holiday schedule!",
    "2025-W01": "🎊 {name} - Happy New Year! First game of 2026!"
  }
}
```

### Timezone Changes

To change from Mexico City time, edit `data/config.json`:

```json
{
  "timezone": "Europe/Madrid"  // or any valid timezone
}
```