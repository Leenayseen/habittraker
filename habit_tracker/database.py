"""SQLite database connection and schema management for the Habit Tracker."""

import sqlite3
import os

DEFAULT_DB_PATH = "data/habits.db"


def get_connection(db_path=DEFAULT_DB_PATH):
    """Return a sqlite3 connection with foreign keys enabled and Row factory.

    Creates the parent directory if it does not exist.
    """
    parent = os.path.dirname(db_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_database(db_path=DEFAULT_DB_PATH):
    """Create habits and completions tables if they do not exist."""
    conn = get_connection(db_path)
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                periodicity TEXT NOT NULL CHECK(periodicity IN ('daily', 'weekly')),
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS completions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER NOT NULL,
                completed_at TEXT NOT NULL,
                FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE
            );
        """)
        conn.commit()
    finally:
        conn.close()
