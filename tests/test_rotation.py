"""Unit tests for rotation logic."""


import pytest

from src.rotation import (
    format_message,
    get_responsible_person,
    get_vacation_coverage,
    get_week_number,
)


class TestRotationBasics:
    """Test basic rotation functionality."""

    def test_get_week_number(self):
        """Test week number extraction."""
        assert get_week_number("2025-W31") == 31
        assert get_week_number("2025-W01") == 1
        assert get_week_number("2025-W52") == 52

    def test_get_week_number_with_padding(self):
        """Test week number with zero padding."""
        assert get_week_number("2025-W09") == 9
        assert get_week_number("2025-W10") == 10


class TestRotationLogic:
    """Test the core rotation logic."""

    @pytest.fixture
    def basic_schedule(self):
        """Basic schedule without overrides."""
        return {
            "default_rotation": ["Esteban", "Chema", "Adrian", "Chito", "Vanish", "JC"],
            "start_week": "2025-W31",
            "schedule_overrides": {},
            "vacation_weeks": {},
            "special_messages": {}
        }

    @pytest.fixture
    def schedule_with_overrides(self):
        """Schedule with various overrides."""
        return {
            "default_rotation": ["Esteban", "Chema", "Adrian", "Chito", "Vanish", "JC"],
            "start_week": "2025-W31",
            "schedule_overrides": {
                "2025-W32": "Adrian",  # Swap
                "2025-W35": "Esteban"  # Another swap
            },
            "vacation_weeks": {
                "Chito": ["2025-W34"],
                "Adrian": ["2025-W40", "2025-W41"]
            },
            "special_messages": {
                "2025-W52": "🎄 Holiday week: {name} is responsible!"
            }
        }

    def test_default_rotation_sequence(self, basic_schedule):
        """Test that rotation follows the default sequence."""
        assert get_responsible_person("2025-W31", basic_schedule)[0] == "Esteban"
        assert get_responsible_person("2025-W32", basic_schedule)[0] == "Chema"
        assert get_responsible_person("2025-W33", basic_schedule)[0] == "Adrian"
        assert get_responsible_person("2025-W34", basic_schedule)[0] == "Chito"
        assert get_responsible_person("2025-W35", basic_schedule)[0] == "Vanish"
        assert get_responsible_person("2025-W36", basic_schedule)[0] == "JC"
        # Should cycle back
        assert get_responsible_person("2025-W37", basic_schedule)[0] == "Esteban"

    def test_schedule_overrides(self, schedule_with_overrides):
        """Test explicit schedule overrides."""
        person32, _ = get_responsible_person("2025-W32", schedule_with_overrides)
        assert person32 == "Adrian"
        person35, _ = get_responsible_person("2025-W35", schedule_with_overrides)
        assert person35 == "Esteban"

    def test_vacation_coverage(self, schedule_with_overrides):
        """Test vacation coverage logic."""
        # Chito is on vacation W34, Vanish should cover
        person, _ = get_responsible_person("2025-W34", schedule_with_overrides)
        assert person == "Vanish"  # Next person in rotation

        # Adrian is on vacation W40 and W41
        # W40 would normally be Chito (40-31=9, 9%6=3 -> Chito)
        # But Adrian is on vacation, so Chito covers
        person, _ = get_responsible_person("2025-W40", schedule_with_overrides)
        assert person == "Chito"  # Next person after Adrian

    def test_special_messages(self, schedule_with_overrides):
        """Test special message handling."""
        person, special_msg = get_responsible_person(
            "2025-W52", schedule_with_overrides
        )
        assert special_msg == "🎄 Holiday week: {name} is responsible!"

    def test_get_vacation_coverage_function(self):
        """Test the vacation coverage helper function."""
        schedule = {
            "default_rotation": ["A", "B", "C", "D"]
        }
        assert get_vacation_coverage("A", "2025-W01", schedule) == "B"
        assert get_vacation_coverage("D", "2025-W01", schedule) == "A"  # Wraps around
        # Z not in rotation
        assert get_vacation_coverage("Z", "2025-W01", schedule) is None


class TestMessageFormatting:
    """Test message formatting functionality."""

    def test_format_basic_message(self):
        """Test basic message formatting."""
        template = "Week {week}: {name} is responsible!"
        result = format_message(template, "Esteban", "2025-W31")
        assert result == "Week 31: Esteban is responsible!"

    def test_format_message_with_special(self):
        """Test formatting with special message override."""
        template = "Regular: {name} for week {week}"
        special = "Special: {name} on week {week}!"
        result = format_message(template, "Chema", "2025-W52", special)
        assert result == "Special: Chema on week 52!"

    def test_format_message_complex_template(self):
        """Test complex message template."""
        template = """Good morning! 🌞

Week {week} Update:
- Responsible: {name}
- Don't forget the balls!

See you on court! 🎾"""

        result = format_message(template, "Adrian", "2025-W33")
        assert "Week 33 Update:" in result
        assert "Responsible: Adrian" in result
        assert "🎾" in result


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_far_future_weeks(self):
        """Test weeks far in the future."""
        schedule = {
            "default_rotation": ["A", "B", "C"],
            "start_week": "2025-W01",
            "schedule_overrides": {},
            "vacation_weeks": {},
            "special_messages": {}
        }
        # 2027-W01 compared to 2025-W01:
        # This is exactly 104 weeks later (2 years * 52 weeks)
        # 104 % 3 = 2, so index 2 = "C"
        person, _ = get_responsible_person("2027-W01", schedule)
        assert person == "C"

    def test_past_weeks(self):
        """Test handling of past weeks."""
        schedule = {
            "default_rotation": ["X", "Y", "Z"],
            "start_week": "2025-W31",
            "schedule_overrides": {},
            "vacation_weeks": {},
            "special_messages": {}
        }
        # Week 30 is before start, but should still calculate correctly
        # 30 - 31 = -1, -1 % 3 = 2
        person, _ = get_responsible_person("2025-W30", schedule)
        assert person == "Z"

    def test_year_boundary(self):
        """Test rotation across year boundaries."""
        schedule = {
            "default_rotation": ["A", "B"],
            "start_week": "2025-W52",
            "schedule_overrides": {},
            "vacation_weeks": {},
            "special_messages": {}
        }
        assert get_responsible_person("2025-W52", schedule)[0] == "A"
        assert get_responsible_person("2026-W01", schedule)[0] == "B"
        assert get_responsible_person("2026-W02", schedule)[0] == "A"
