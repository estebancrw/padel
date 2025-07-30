# Padel Bot Project Plan

## Project Overview
A Telegram bot that sends automated messages to a group on a rotating weekly schedule (Sunday, Monday, Tuesday at 9am CST) using GitHub Actions for scheduling.

## Architecture Components

### 1. Telegram Bot Setup
- **Platform**: Telegram Bot API
- **Library**: `python-telegram-bot` (27.9k stars, enterprise-grade, v22.3 July 2025)
- **Authentication**: Bot token from @BotFather
- **Target**: Telegram group with bot added as member

### 2. Scheduling System
- **Platform**: GitHub Actions with cron scheduling
- **Schedule**: `0 15 * * 0,1,2` (15:00 UTC = 9:00 AM Mexico City Time)
- **Frequency**: 3 times per week (Sunday, Monday, Tuesday)

### 3. Message Rotation Logic
- **Storage**: JSON configuration file with schedule overrides and defaults
- **Algorithm**: Hybrid approach - check overrides first, fallback to rotation calculation
- **Flexibility**: Supports vacations, swaps, and special events
- **Persistence**: Git-based configuration management

## Technical Implementation

### File Structure
```
padel-bot/
├── .github/workflows/
│   ├── send-message.yml          # Production workflow
│   └── test.yml                  # CI/CD testing workflow
├── src/
│   ├── __init__.py
│   ├── bot.py                    # Main bot script
│   ├── rotation.py               # Rotation logic
│   └── config.py                 # Configuration management
├── tests/
│   ├── __init__.py
│   ├── test_rotation.py          # Unit tests for rotation logic
│   ├── test_bot.py               # Unit tests for bot functionality
│   └── test_config.py            # Unit tests for config management
├── scripts/
│   ├── generate_schedule.py      # Generate yearly schedule
│   └── manage_schedule.py        # Schedule management CLI
├── data/
│   ├── schedule_2025.json        # Weekly schedule with overrides
│   └── config.json               # Bot configuration
├── docs/
│   ├── BOT.md                    # Bot development guide
│   └── API.md                    # Function documentation
├── pyproject.toml                # uv project configuration & dependencies
├── uv.lock                       # uv lockfile (auto-generated)
├── .python-version               # Python version specification
├── README.md                     # Project overview
├── ruff.toml                     # Linter configuration
└── .gitignore                    # Git ignore rules
```

### Python Dependencies (pyproject.toml)
```toml
[project]
name = "padel-bot"
version = "0.1.0"
description = "Telegram bot for Padel group rotation scheduling"
readme = "README.md"
requires-python = ">=3.9"
dependencies = [
    "python-telegram-bot==22.3"
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=5.0.0",
    "ruff>=0.5.0",
    "mypy>=1.10.0",
    "types-pytz"
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 88
target-version = "py39"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
addopts = "--cov=src --cov-report=html --cov-report=term"

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

### Environment Variables & Secrets
- `TELEGRAM_BOT_TOKEN` - Bot authentication token (GitHub Secret)
- `TELEGRAM_CHAT_ID` - Target group chat ID (GitHub Secret)
- `ROTATION_CONFIG` - JSON string with rotation data (GitHub Variable)

## Development Best Practices

### Code Quality Standards

#### Linting & Formatting
- **Ruff**: Fast Python linter combining multiple tools
- **Line length**: 88 characters (Black standard)
- **Import sorting**: Automatic with isort rules
- **Type checking**: MyPy with strict mode

```bash
# Run linting
uv run ruff check src/ tests/

# Auto-fix issues
uv run ruff check --fix src/ tests/

# Type checking
uv run mypy src/
```

#### Testing Requirements
- **Minimum coverage**: 80% for all modules
- **Test categories**: Unit, integration, edge cases
- **Async testing**: pytest-asyncio for Telegram API
- **Mocking**: Mock external API calls

```bash
# Run all tests with coverage
uv run pytest

# Run specific test file
uv run pytest tests/test_rotation.py -v

# Generate HTML coverage report
uv run pytest --cov-report=html
```

### CI/CD Pipeline

#### GitHub Actions Test Workflow (.github/workflows/test.yml)
```yaml
name: Test Suite
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install uv
        uses: astral-sh/setup-uv@v6
      - name: Set up Python
        run: uv python install
      - name: Install dependencies
        run: uv sync --all-extras
      - name: Lint with ruff
        run: uv run ruff check src/ tests/
      - name: Type check with mypy
        run: uv run mypy src/
      - name: Run tests
        run: uv run pytest
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### Documentation Structure

#### README.md
- Project overview and purpose
- Quick start guide
- Architecture diagram
- Contributing guidelines

#### docs/BOT.md
- Development setup instructions
- Testing locally with ngrok
- Telegram bot configuration
- Troubleshooting guide

#### docs/API.md
- Function signatures and docstrings
- Module structure
- Example usage patterns

## Production Best Practices

### Security
- ✅ Use GitHub Secrets for sensitive data (tokens, chat IDs)
- ✅ Environment-specific secrets for different deployment stages
- ✅ Regular secret rotation (30-90 days)
- ✅ Least privilege access principles
- ✅ Secret masking in logs

### Error Handling & Reliability
- ✅ Exponential backoff for rate limit errors (429)
- ✅ Retry logic with maximum attempts (3 retries)
- ✅ Comprehensive error logging
- ✅ Graceful failure handling
- ✅ Rate limit compliance (max 1 message/second per chat)

### Monitoring & Observability
- ✅ GitHub Actions run history for execution tracking
- ✅ Error notifications via workflow failure alerts
- ✅ Message delivery confirmation logging
- ✅ Weekly rotation state tracking

### Rate Limiting Strategy
- **Telegram Limits**: 30 requests/second, 20 messages/minute per chat
- **Implementation**: Single message per execution (well within limits)
- **Safety**: Built-in retry mechanism with exponential backoff

## Implementation Phases

### Phase 1: Core Setup
1. Create Telegram bot via @BotFather
2. Set up GitHub repository with secrets
3. Initialize uv project with `uv init`
4. Implement basic message sending functionality
5. Create initial GitHub Actions workflow with uv support

### Phase 2: Rotation Logic
1. Create schedule JSON with overrides
2. Implement hybrid rotation algorithm (overrides + fallback)
3. Add vacation and swap handling
4. Create schedule modification helper script
5. Test edge cases (vacations, year boundaries)

### Phase 3: Production Hardening
1. Add comprehensive error handling
2. Implement retry mechanisms
3. Add logging and monitoring
4. Security audit and testing

### Phase 4: Testing & Deployment
1. End-to-end testing with test group
2. Schedule validation across time zones
3. Production deployment
4. Monitoring setup

## Testing Strategy

### Manual Testing Methods

#### 1. Workflow Dispatch (Manual Trigger)
The GitHub Actions workflow includes `workflow_dispatch` trigger for manual testing:

```yaml
on:
  schedule:
    - cron: '0 15 * * 0,1,2'  # Scheduled runs
  workflow_dispatch:          # Manual trigger
    inputs:
      test_message:
        description: 'Optional test message override'
        required: false
        type: string
      force_week:
        description: 'Force specific week number for rotation testing'
        required: false
        type: number
```

**How to test manually:**
1. Go to GitHub repository → Actions tab
2. Select "Send Padel Message" workflow
3. Click "Run workflow" button
4. Optionally provide test inputs
5. Click "Run workflow" to execute immediately

#### 2. Testing Different Rotation States
To test weekly rotation without waiting:

```bash
# Test specific week numbers locally
python src/bot.py --test-week 1
python src/bot.py --test-week 2
python src/bot.py --test-week 3
```

#### 3. Dry Run Mode
Implement dry-run functionality for safe testing:

```bash
# Test without sending actual messages
python src/bot.py --dry-run
```

### Test Group Setup
1. **Create test group**: Set up separate Telegram group for testing
2. **Test bot token**: Use same bot but different `TELEGRAM_CHAT_ID` for test group
3. **Environment secrets**: 
   - `TELEGRAM_CHAT_ID_TEST` - Test group chat ID
   - Use repository variables to switch between test/prod

### Validation Checklist
- ✅ Bot can send messages to test group
- ✅ Rotation logic cycles through all messages
- ✅ Timezone conversion works correctly (CST to UTC)
- ✅ Error handling works (invalid chat ID, network issues)
- ✅ Manual trigger executes immediately
- ✅ Scheduled runs execute at correct times
- ✅ Message formatting displays correctly

### Testing Commands Reference

#### GitHub Actions Manual Trigger
```bash
# Via GitHub CLI (if installed)
gh workflow run send-message.yml

# With inputs
gh workflow run send-message.yml -f test_message="Test message" -f force_week=1
```

#### Local Testing Setup
```bash
# Set environment variables
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_test_chat_id"

# Using uv (recommended)
uv run src/bot.py --test
uv run src/bot.py --dry-run --week 5

# Or with traditional Python (if uv not available)
python src/bot.py --test
python src/bot.py --dry-run --week 5
```

#### GitHub Actions Workflow Updates for uv
```yaml
name: Send Padel Message
on:
  schedule:
    - cron: '0 15 * * 0,1,2'  # 15:00 UTC = 9:00 AM Mexico City
  workflow_dispatch:
    inputs:
      test_message:
        description: 'Optional test message override' 
        required: false
        type: string
      force_week:
        description: 'Force specific week number for rotation testing'
        required: false
        type: number

jobs:
  send-message:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install uv
        uses: astral-sh/setup-uv@v6
        
      - name: Set up Python
        run: uv python install
        
      - name: Install dependencies
        run: uv sync
        
      - name: Send Telegram message
        env:
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
          TEST_MESSAGE: ${{ inputs.test_message }}
          FORCE_WEEK: ${{ inputs.force_week }}
        run: uv run src/bot.py
```

### Monitoring Test Results
- **GitHub Actions logs**: Check workflow execution logs
- **Telegram message delivery**: Verify messages appear in test group
- **Error notifications**: Confirm failure alerts work
- **Rotation tracking**: Validate week-over-week message changes

## Configuration Schema

### Schedule Configuration (data/schedule_2025.json)
```json
{
  "default_rotation": ["Esteban", "Chema", "Adrian", "Chito", "Vanish", "JC"],
  "start_week": "2025-W31",
  "schedule_overrides": {
    "2025-W31": "Esteban",
    "2025-W32": "Chema",
    "2025-W33": "Adrian",
    "2025-W34": "Chito",
    "2025-W35": "Vanish",
    "2025-W36": "JC",
    "2025-W37": "Esteban",
    "2025-W38": "Chema"
    // Add more weeks as needed or handle swaps
  },
  "vacation_weeks": {
    "Chito": ["2025-W40"],
    "Adrian": ["2025-W45", "2025-W46"]
  },
  "special_messages": {
    "2025-W52": "🎄 Holiday week: {name} is responsible (confirm schedule!)"
  }
}
```

### Bot Configuration (data/config.json)
```json
{
  "timezone": "America/Mexico_City",
  "group_name": "Padel Group",
  "message_template": "Good morning! Today's reminders:\n\n🏓 Week {week}: {name} is responsible for court booking today! 🎾\n\nDon't forget:\n• Confirm attendance\n• Bring water and towels\n• Check weather conditions\n\nSee you on the court! 🎾",
  "schedule": {
    "days": ["Sunday", "Monday", "Tuesday"],
    "time": "09:00"
  }
}
```

## Schedule Management

### Rotation Algorithm
```python
def get_responsible_person(week_string, schedule_data):
    """
    Hybrid approach: Check overrides first, then calculate from default rotation
    """
    # 1. Check for vacation coverage
    for person, vacation_weeks in schedule_data.get("vacation_weeks", {}).items():
        if week_string in vacation_weeks:
            # Find next person in rotation to cover
            return get_vacation_coverage(person, week_string, schedule_data)
    
    # 2. Check explicit overrides
    if week_string in schedule_data.get("schedule_overrides", {}):
        return schedule_data["schedule_overrides"][week_string]
    
    # 3. Calculate from default rotation
    week_number = int(week_string.split("-W")[1])
    start_week = int(schedule_data["start_week"].split("-W")[1])
    rotation_index = (week_number - start_week) % len(schedule_data["default_rotation"])
    return schedule_data["default_rotation"][rotation_index]
```

### Making Schedule Changes

#### Easy Modifications via JSON:
1. **Swap weeks**: Edit `schedule_overrides` section
2. **Add vacation**: Add to `vacation_weeks` with automatic coverage
3. **Special events**: Add to `special_messages` for custom notifications

#### Example: Handling a Swap
```json
// Before: Week 34 is Chito's turn
"2025-W34": "Chito",

// After: Adrian and Chito swap weeks
"2025-W34": "Adrian",  // Adrian covers for Chito
"2025-W36": "Chito",   // Chito takes Adrian's week
```

### Schedule Helper Script
```bash
# Generate schedule for the year
uv run scripts/generate_schedule.py --year 2025

# Add vacation
uv run scripts/manage_schedule.py add-vacation --person "Chito" --week "2025-W40"

# Swap weeks
uv run scripts/manage_schedule.py swap --week1 "2025-W34" --week2 "2025-W36"

# View upcoming schedule
uv run scripts/manage_schedule.py show --weeks 8
```

### Example Unit Tests

#### test_rotation.py
```python
import pytest
from datetime import date
from src.rotation import get_responsible_person, get_week_string

class TestRotation:
    def test_default_rotation(self):
        """Test basic rotation without overrides"""
        schedule = {
            "default_rotation": ["Esteban", "Chema", "Adrian"],
            "start_week": "2025-W31"
        }
        assert get_responsible_person("2025-W31", schedule) == "Esteban"
        assert get_responsible_person("2025-W32", schedule) == "Chema"
        assert get_responsible_person("2025-W33", schedule) == "Adrian"
        assert get_responsible_person("2025-W34", schedule) == "Esteban"  # Cycles back
    
    def test_schedule_override(self):
        """Test explicit schedule overrides"""
        schedule = {
            "default_rotation": ["Esteban", "Chema", "Adrian"],
            "start_week": "2025-W31",
            "schedule_overrides": {
                "2025-W32": "Adrian"  # Swap
            }
        }
        assert get_responsible_person("2025-W32", schedule) == "Adrian"
    
    def test_vacation_handling(self):
        """Test vacation coverage logic"""
        schedule = {
            "default_rotation": ["Esteban", "Chema", "Adrian"],
            "start_week": "2025-W31",
            "vacation_weeks": {
                "Chema": ["2025-W32"]
            }
        }
        # Next person should cover
        assert get_responsible_person("2025-W32", schedule) == "Adrian"
```

## Risk Assessment & Mitigation

### Technical Risks
- **GitHub Actions downtime**: Minimal impact, messages can be sent manually
- **Telegram API rate limits**: Implemented backoff and retry logic
- **Bot token compromise**: Regular rotation and monitoring procedures

### Operational Risks
- **Incorrect scheduling**: Comprehensive testing across time zones
- **Message repetition**: Week-based rotation with state tracking
- **Group membership changes**: Bot permission monitoring

## Success Metrics
- **Reliability**: >99% successful message delivery
- **Accuracy**: Correct rotation without repetition
- **Timeliness**: Messages sent within 5 minutes of scheduled time
- **Maintainability**: Easy configuration updates without code changes

## Future Enhancements
- Web dashboard for rotation management
- Multiple group support
- Custom message templates
- Holiday scheduling exceptions
- Integration with calendar systems