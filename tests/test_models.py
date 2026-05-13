import pytest
from datetime import datetime
from habit_tracker.models import Habit, DAILY, WEEKLY, VALID_PERIODICITIES


class TestHabit:
    def test_creates_valid_habit(self):
        habit = Habit("Drink water", "Drink 2L", DAILY)
        assert habit.name == "Drink water"
        assert habit.description == "Drink 2L"
        assert habit.periodicity == DAILY
        assert habit.created_at is not None
        assert habit.id is None

    def test_rejects_empty_name(self):
        with pytest.raises(ValueError):
            Habit("", "desc", DAILY)

    def test_rejects_invalid_periodicity(self):
        with pytest.raises(ValueError):
            Habit("Run", "desc", "monthly")

    def test_auto_generates_created_at(self):
        habit = Habit("Read", "Read 10 pages", DAILY)
        parsed = datetime.fromisoformat(habit.created_at)
        assert parsed.date() == datetime.now().date()

    def test_accepts_explicit_created_at(self):
        ts = "2026-01-01T09:00:00"
        habit = Habit("Walk", "Walk 20 min", DAILY, created_at=ts)
        assert habit.created_at == ts

    def test_accepts_habit_id(self):
        habit = Habit("Test", "", DAILY, habit_id=42)
        assert habit.id == 42

    def test_valid_periodicities(self):
        assert VALID_PERIODICITIES == {"daily", "weekly"}

    def test_weekly_periodicity(self):
        habit = Habit("Review", "Weekly review", WEEKLY)
        assert habit.periodicity == "weekly"

    def test_default_description(self):
        habit = Habit("Test", periodicity=DAILY)
        assert habit.description == ""
