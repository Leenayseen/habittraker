from datetime import datetime, date, timedelta
import datetime as _dt

from habit_tracker.models import DAILY, WEEKLY


def _parse_date(value):
    """Parse an ISO timestamp string into a date object."""
    return datetime.fromisoformat(value).date()


def get_all_habits(habits):
    """Return all currently tracked habits."""
    return list(habits)


def get_habits_by_periodicity(habits, periodicity):
    """Return habits matching the selected periodicity."""
    return list(filter(lambda h: h.periodicity == periodicity, habits))


def _longest_daily_streak(completions):
    """Calculate the longest streak of consecutive days from completion timestamps."""
    if not completions:
        return 0
    days = sorted(set(_parse_date(c) for c in completions))
    longest = 1
    current = 1
    for i in range(1, len(days)):
        if (days[i] - days[i - 1]).days == 1:
            current += 1
            longest = max(longest, current)
        else:
            current = 1
    return longest


def _longest_weekly_streak(completions):
    """Calculate the longest streak of consecutive ISO calendar weeks."""
    if not completions:
        return 0
    weeks = sorted(set(_parse_date(c).isocalendar()[:2] for c in completions))
    longest = 1
    current = 1
    for i in range(1, len(weeks)):
        prev_year, prev_week = weeks[i - 1]
        curr_year, curr_week = weeks[i]
        expected_next = prev_week + 1
        if expected_next > 52:
            prev_iso = date.fromisocalendar(prev_year, prev_week, 1)
            next_week_start = prev_iso + timedelta(weeks=1)
            expected_year, expected_week = next_week_start.isocalendar()[:2]
        else:
            expected_year, expected_week = prev_year, expected_next
        if curr_year == expected_year and curr_week == expected_week:
            current += 1
            longest = max(longest, current)
        else:
            current = 1
    return longest


def get_longest_streak_for_habit(habit, completions):
    """Return the longest streak for one habit based on its periodicity."""
    if not completions:
        return 0
    if habit.periodicity == DAILY:
        return _longest_daily_streak(completions)
    return _longest_weekly_streak(completions)


def get_longest_streak_all(habits, completions_by_habit):
    """Return the longest streak number among all habits."""
    if not habits:
        return 0
    streaks = [get_longest_streak_for_habit(h, completions_by_habit.get(h.name, [])) for h in habits]
    return max(streaks) if streaks else 0
