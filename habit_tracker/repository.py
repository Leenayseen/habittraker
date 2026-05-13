"""Data access layer for habits and completions.

All functions accept an optional db_path parameter and return
Habit objects or primitive values.
"""

from datetime import datetime

from habit_tracker.models import Habit
from habit_tracker.database import DEFAULT_DB_PATH, get_connection, initialize_database


def _row_to_habit(row):
    """Convert a sqlite3.Row to a Habit object."""
    return Habit(
        name=row["name"],
        description=row["description"],
        periodicity=row["periodicity"],
        created_at=row["created_at"],
        habit_id=row["id"],
    )


def create_habit(name, description="", periodicity="daily", db_path=DEFAULT_DB_PATH):
    """Create a new habit in the database and return the Habit object."""
    initialize_database(db_path)
    habit = Habit(name=name, description=description, periodicity=periodicity)
    conn = get_connection(db_path)
    try:
        cursor = conn.execute(
            "INSERT INTO habits (name, description, periodicity, created_at) VALUES (?, ?, ?, ?)",
            (habit.name, habit.description, habit.periodicity, habit.created_at),
        )
        conn.commit()
        habit.id = cursor.lastrowid
        return habit
    finally:
        conn.close()


def get_all_habits(db_path=DEFAULT_DB_PATH):
    """Return all habits from the database as Habit objects."""
    initialize_database(db_path)
    conn = get_connection(db_path)
    try:
        rows = conn.execute("SELECT * FROM habits").fetchall()
        return [_row_to_habit(row) for row in rows]
    finally:
        conn.close()


def get_habit_by_name(name, db_path=DEFAULT_DB_PATH):
    """Return a single habit matching the given name, or None."""
    initialize_database(db_path)
    conn = get_connection(db_path)
    try:
        row = conn.execute("SELECT * FROM habits WHERE name = ?", (name,)).fetchone()
        if row is None:
            return None
        return _row_to_habit(row)
    finally:
        conn.close()


def delete_habit(identifier, db_path=DEFAULT_DB_PATH):
    """Delete a habit by name or numeric ID. Return True if a row was deleted."""
    initialize_database(db_path)
    conn = get_connection(db_path)
    try:
        try:
            habit_id = int(identifier)
            cursor = conn.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
        except (ValueError, TypeError):
            cursor = conn.execute("DELETE FROM habits WHERE name = ?", (identifier,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def add_completion(habit_id, completed_at=None, db_path=DEFAULT_DB_PATH):
    """Store a completion timestamp for the given habit."""
    initialize_database(db_path)
    ts = completed_at or datetime.now().isoformat(timespec="seconds")
    conn = get_connection(db_path)
    try:
        conn.execute(
            "INSERT INTO completions (habit_id, completed_at) VALUES (?, ?)",
            (habit_id, ts),
        )
        conn.commit()
    finally:
        conn.close()


def get_completions_for_habit(habit_id, db_path=DEFAULT_DB_PATH):
    """Return completion timestamps for a habit as a list of ISO strings."""
    initialize_database(db_path)
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            "SELECT completed_at FROM completions WHERE habit_id = ? ORDER BY completed_at",
            (habit_id,),
        ).fetchall()
        return [row["completed_at"] for row in rows]
    finally:
        conn.close()


def get_completions_grouped_by_habit(db_path=DEFAULT_DB_PATH):
    """Return a dict mapping habit_id to a list of completion ISO strings."""
    initialize_database(db_path)
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            "SELECT habit_id, completed_at FROM completions ORDER BY completed_at"
        ).fetchall()
        grouped = {}
        for row in rows:
            grouped.setdefault(row["habit_id"], []).append(row["completed_at"])
        return grouped
    finally:
        conn.close()
