import pytest
from habit_tracker.models import Habit, DAILY, WEEKLY
from habit_tracker.analytics import (
    get_all_habits,
    get_habits_by_periodicity,
    get_longest_streak_for_habit,
    get_longest_streak_all,
)


def _make_habit(name, periodicity=DAILY):
    return Habit(name=name, periodicity=periodicity)


class TestGetAllHabits:
    def test_returns_all(self):
        habits = [_make_habit("A"), _make_habit("B")]
        assert get_all_habits(habits) == habits

    def test_empty(self):
        assert get_all_habits([]) == []


class TestFilterByPeriodicity:
    def test_daily(self):
        habits = [_make_habit("A", DAILY), _make_habit("B", WEEKLY)]
        result = get_habits_by_periodicity(habits, DAILY)
        assert len(result) == 1
        assert result[0].name == "A"

    def test_weekly(self):
        habits = [_make_habit("A", DAILY), _make_habit("B", WEEKLY)]
        result = get_habits_by_periodicity(habits, WEEKLY)
        assert len(result) == 1
        assert result[0].name == "B"

    def test_no_match(self):
        habits = [_make_habit("A", DAILY)]
        result = get_habits_by_periodicity(habits, WEEKLY)
        assert result == []


class TestDailyStreak:
    def test_consecutive_days(self):
        habit = _make_habit("Test", DAILY)
        completions = ["2026-01-01T09:00:00", "2026-01-02T10:00:00", "2026-01-03T08:00:00"]
        assert get_longest_streak_for_habit(habit, completions) == 3

    def test_missing_day_breaks_streak(self):
        habit = _make_habit("Test", DAILY)
        completions = ["2026-01-01T09:00:00", "2026-01-02T09:00:00", "2026-01-04T09:00:00"]
        assert get_longest_streak_for_habit(habit, completions) == 2

    def test_empty_completions(self):
        habit = _make_habit("Test", DAILY)
        assert get_longest_streak_for_habit(habit, []) == 0

    def test_single_completion(self):
        habit = _make_habit("Test", DAILY)
        assert get_longest_streak_for_habit(habit, ["2026-01-01T09:00:00"]) == 1


class TestWeeklyStreak:
    def test_consecutive_weeks(self):
        habit = _make_habit("Test", WEEKLY)
        completions = ["2026-01-06T09:00:00", "2026-01-13T09:00:00", "2026-01-20T09:00:00"]
        assert get_longest_streak_for_habit(habit, completions) == 3

    def test_missing_week_breaks_streak(self):
        habit = _make_habit("Test", WEEKLY)
        completions = ["2026-01-06T09:00:00", "2026-01-13T09:00:00", "2026-01-27T09:00:00"]
        assert get_longest_streak_for_habit(habit, completions) == 2

    def test_empty_completions(self):
        habit = _make_habit("Test", WEEKLY)
        assert get_longest_streak_for_habit(habit, []) == 0


class TestLongestStreakAll:
    def test_multiple_habits(self):
        h1 = _make_habit("A", DAILY)
        h2 = _make_habit("B", DAILY)
        completions_by_habit = {
            h1.name: ["2026-01-01T09:00:00", "2026-01-02T09:00:00"],
            h2.name: ["2026-01-01T09:00:00", "2026-01-02T09:00:00", "2026-01-03T09:00:00"],
        }
        assert get_longest_streak_all([h1, h2], completions_by_habit) == 3

    def test_empty(self):
        assert get_longest_streak_all([], {}) == 0


class TestDuplicateCompletionsCountOnce:
    def test_daily_duplicates(self):
        habit = _make_habit("Test", DAILY)
        completions = ["2026-01-01T09:00:00", "2026-01-01T15:00:00", "2026-01-02T09:00:00"]
        assert get_longest_streak_for_habit(habit, completions) == 2

    def test_weekly_duplicates(self):
        habit = _make_habit("Test", WEEKLY)
        completions = ["2026-01-06T09:00:00", "2026-01-08T09:00:00", "2026-01-13T09:00:00"]
        assert get_longest_streak_for_habit(habit, completions) == 2
