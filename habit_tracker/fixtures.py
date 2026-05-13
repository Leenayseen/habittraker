"""Predefined habits and four weeks of sample tracking data."""

from datetime import datetime, timedelta

from habit_tracker.database import DEFAULT_DB_PATH, get_connection, initialize_database
from habit_tracker.repository import create_habit, add_completion, get_all_habits

PREDEFINED_HABITS = [
    {"name": "Drink Water", "description": "Drink at least 2 liters of water", "periodicity": "daily"},
    {"name": "Read 10 Pages", "description": "Read at least 10 pages of a book", "periodicity": "daily"},
    {"name": "Morning Walk", "description": "Walk for at least 20 minutes", "periodicity": "daily"},
    {"name": "Weekly Review", "description": "Review weekly goals and tasks", "periodicity": "weekly"},
    {"name": "Clean Workspace", "description": "Clean and organize the workspace", "periodicity": "weekly"},
]


def _generate_fixture_completions(start_date, daily_names, weekly_names):
    """Generate four weeks of completion timestamps with intentional gaps.

    Returns a list of (habit_name, iso_timestamp) tuples.
    """
    completions = []
    for week_offset in range(4):
        week_start = start_date + timedelta(weeks=week_offset)
        for day_offset in range(7):
            date = week_start + timedelta(days=day_offset)
            if date.weekday() == 3 and week_offset == 1:
                continue
            ts = date.replace(hour=9, minute=0, second=0).isoformat(timespec="seconds")
            for name in daily_names:
                completions.append((name, ts))
        weekly_ts = week_start.replace(hour=10, minute=0, second=0).isoformat(timespec="seconds")
        if week_offset == 2:
            weekly_ts = None
        if weekly_ts:
            for name in weekly_names:
                completions.append((name, weekly_ts))
    return completions


def load_fixtures(reset=False, db_path=DEFAULT_DB_PATH):
    """Load predefined habits and four weeks of sample completion data.

    Args:
        reset: If True, delete all existing habits and completions before loading.
        db_path: Path to the SQLite database file.

    Returns:
        The number of new habits created.
    """
    initialize_database(db_path)
    conn = get_connection(db_path)
    try:
        if reset:
            conn.execute("DELETE FROM completions")
            conn.execute("DELETE FROM habits")
            conn.commit()
    finally:
        conn.close()

    existing = {h.name for h in get_all_habits(db_path)}
    created = 0
    habit_map = {}
    for spec in PREDEFINED_HABITS:
        if spec["name"] not in existing:
            habit = create_habit(spec["name"], spec["description"], spec["periodicity"], db_path)
            created += 1
        else:
            from habit_tracker.repository import get_habit_by_name
            habit = get_habit_by_name(spec["name"], db_path)
        habit_map[spec["name"]] = habit

    if created > 0:
        daily_names = [s["name"] for s in PREDEFINED_HABITS if s["periodicity"] == "daily"]
        weekly_names = [s["name"] for s in PREDEFINED_HABITS if s["periodicity"] == "weekly"]
        start = datetime(2026, 4, 6)
        completions = _generate_fixture_completions(start, daily_names, weekly_names)
        for name, ts in completions:
            habit = habit_map.get(name)
            if habit:
                add_completion(habit.id, ts, db_path)

    return created
