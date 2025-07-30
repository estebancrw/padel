"""Rotation logic for determining who's responsible each week."""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from zoneinfo import ZoneInfo


def load_schedule_data(schedule_path: Path) -> dict:
    """Load schedule data from JSON file."""
    with open(schedule_path, encoding="utf-8") as f:
        return json.load(f)  # type: ignore[no-any-return]


def get_current_week_string(timezone: str = "America/Mexico_City") -> str:
    """Get the current ISO week string (e.g., '2025-W31')."""
    now = datetime.now(ZoneInfo(timezone))
    year, week, _ = now.isocalendar()
    return f"{year}-W{week:02d}"


def get_week_number(week_string: str) -> int:
    """Extract week number from ISO week string."""
    return int(week_string.split("-W")[1])


def get_total_weeks_since_epoch(week_string: str) -> int:
    """Calculate total weeks since a fixed epoch for consistent ordering."""
    year_str, week_str = week_string.split("-W")
    year_int = int(year_str)
    week_int = int(week_str)
    # Use a simple formula: (year - 2000) * 52 + week
    # This isn't perfect for leap weeks but good enough for rotation
    return (year_int - 2000) * 52 + week_int


def get_vacation_coverage(
    person: str, week_string: str, schedule_data: dict
) -> Optional[str]:
    """Find who covers for someone on vacation."""
    # Get the default rotation position of the person on vacation
    rotation = schedule_data["default_rotation"]
    if person not in rotation:
        return None

    person_index = rotation.index(person)
    # Next person in rotation covers
    next_index = (person_index + 1) % len(rotation)
    return str(rotation[next_index])


def get_responsible_person(
    week_string: str, schedule_data: dict
) -> tuple[str, Optional[str]]:
    """
    Get responsible person for a given week.

    Returns tuple of (person_name, special_message)
    """
    # Check for special messages
    special_message = schedule_data.get("special_messages", {}).get(week_string)

    # Check for vacation coverage
    for person, vacation_weeks in schedule_data.get("vacation_weeks", {}).items():
        if week_string in vacation_weeks:
            # Find next person in rotation to cover
            coverage = get_vacation_coverage(person, week_string, schedule_data)
            if coverage:
                return coverage, special_message

    # Check explicit overrides
    if week_string in schedule_data.get("schedule_overrides", {}):
        return schedule_data["schedule_overrides"][week_string], special_message

    # Calculate from default rotation
    total_weeks = get_total_weeks_since_epoch(week_string)
    start_total_weeks = get_total_weeks_since_epoch(schedule_data["start_week"])
    weeks_since_start = total_weeks - start_total_weeks

    rotation = schedule_data["default_rotation"]
    rotation_index = weeks_since_start % len(rotation)

    return rotation[rotation_index], special_message


def format_message(
    template: str, name: str, week_string: str, special_message: Optional[str] = None
) -> str:
    """Format the message template with current data."""
    week_number = get_week_number(week_string)

    # Use special message if available, otherwise use template
    if special_message:
        message = special_message.format(name=name, week=week_number)
    else:
        message = template.format(name=name, week=week_number)

    return message
